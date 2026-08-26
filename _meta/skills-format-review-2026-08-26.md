# Skills Format Review (2026-08-26)
> Compared `skills/` against Anthropic's official Agent Skills / Claude Code spec. Verdict: does not conform. Pending owner review.

## Summary
This repo's `skills/` folder is a useful reference library, but structurally it is not set up as installable Claude Code Skills — none of it would be auto-discovered or auto-triggered as-is.

## Findings

1. **Wrong location.** Claude Code only discovers skills from `~/.claude/skills/`, `.claude/skills/` (project, incl. nested), or a plugin's `skills/` folder. This repo's `skills/` sits at repo root, which is never scanned.

2. **Broken YAML frontmatter — `skills/coding-guidelines/SKILL.md`.** Opens with three `---` in a row, then fields written as Markdown bold (`**name**: ...`, `**descriptions**: ...`) instead of real `key: value` YAML. A parser sees an empty frontmatter block; `description` — "the only content Claude sees before deciding whether to load the full skill" — never gets parsed. Key name is also misspelled (`descriptions` vs `description`).

3. **Fabricated frontmatter field.** `**user-invocable**: false` is not a real Claude Code field. The documented mechanism is `disable-model-invocation: true`. `skills/core-actionbook/SKILL.md` has the same intent but achieves it by omitting `description` entirely, which isn't a documented control.

4. **`skills/webapp-testing/` — good content, wrong filename.** Frontmatter (`name`/`description`/`license`/`tags`) is valid and the `scripts/`/`examples/` layout matches recommended structure, but the file is named `Web Application Testing.md` instead of the required `SKILL.md`, so it's never picked up even if relocated to `.claude/skills/`.

5. **Missing resource linkage.** `coding-guidelines/SKILL.md` doesn't reference its sibling files (`index/rules-index.md`, `clippy-lints/_index.md`) in an "Additional Resources" section, so Claude wouldn't know to load them even with valid frontmatter.

6. **`drawio-skill` git submodule — non-standard but not wrong.** Reasonable for version-pinned reuse, but Anthropic's sanctioned distribution path for sharing a skill across repos is a plugin (`.claude-plugin/plugin.json`) via a marketplace, or a symlink into `.claude/skills/`. A submodule under an undiscovered `skills/` folder gets version control, not actual Claude Code integration, unless separately symlinked/copied into `.claude/skills/`.

## To actually conform
- Move skills to `.claude/skills/<name>/SKILL.md`.
- Fix YAML frontmatter to real `key: value` pairs; correct `descriptions` → `description`.
- Rename `Web Application Testing.md` → `SKILL.md`.
- Replace `user-invocable: false` with `disable-model-invocation: true`.
- Add an "Additional Resources" section in `SKILL.md` bodies linking sibling files.

## Sources
- [Extend Claude with skills - Claude Code Docs](https://code.claude.com/docs/en/skills)
- [claude-code skill-development SKILL.md](https://github.com/anthropics/claude-code/blob/main/plugins/plugin-dev/skills/skill-development/SKILL.md?plain=1)
- [Claude Code Skill Frontmatter: Every YAML Option Explained](https://allahabadi.dev/blogs/ai/claude-code-skills-frontmatter-complete-guide/)
- [Inside Claude Code Skills: Structure, prompts, invocation | Mikhail Shilkov](https://mikhail.io/2025/10/claude-code-skills/)
