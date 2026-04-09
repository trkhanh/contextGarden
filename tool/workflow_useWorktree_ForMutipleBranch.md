# Leveraging Git Worktree for Parallel Agent Development

**Goal:** Run multiple agents simultaneously on different branches/issues within the same local machine to accelerate development velocity.

---

## Overview

Git worktree allows you to work on multiple branches concurrently without switching contexts. Each worktree is an independent working directory pointing to different branches, enabling:

✅ **Parallel Development** - Multiple agents working on different issues simultaneously  
✅ **No Context Switching** - Each worktree maintains its own state and environment  
✅ **Faster CI/CD** - Changes can be tested in parallel before integration  
✅ **Reduced Merge Conflicts** - Isolated work reduces cross-branch interference  

---

## Core Concepts

### Worktree vs. Branches

| Aspect | Branch Only | Branch + Worktree |
|--------|------------|------------------|
| Parallel work | ❌ Must switch | ✅ Simultaneous |
| Build time | Sequential | Parallelizable |
| IDE state | Single context | Multiple contexts |
| Memory usage | Low | Higher (multiple dirs) |

---

## Setup & Workflow

### 1. Initial Repository Setup

```bash
# Clone main repository
git clone git@github.com:trkhanh/contextGarden.git
cd contextGarden

# Ensure main branch is up to date
git fetch origin
git checkout main
git pull origin main
```

### 2. Create Worktrees for Each Issue

#### Pattern: One Worktree Per Agent/Issue

```bash
# Create worktree for feature/agent-1
git worktree add ../contextGarden-agent-1 -b feature/agent-1 origin/main

# Create worktree for bugfix/issue-42
git worktree add ../contextGarden-issue-42 -b bugfix/issue-42 origin/main

# Create worktree for task/refactor-skills
git worktree add ../contextGarden-refactor -b task/refactor-skills origin/main
```

**Result:**
```
contextGarden/          (main branch)
contextGarden-agent-1/  (feature/agent-1)
contextGarden-issue-42/ (bugfix/issue-42)
contextGarden-refactor/ (task/refactor-skills)
```

### 3. List Active Worktrees

```bash
# See all worktrees and their branches
git worktree list

# Output:
# /home/kane/Workspaces/contextGarden       dc4fa80 [main]
# /home/kane/Workspaces/contextGarden-agent-1   abc1234 [feature/agent-1]
# /home/kane/Workspaces/contextGarden-issue-42  def5678 [bugfix/issue-42]
# /home/kane/Workspaces/contextGarden-refactor  ghi9012 [task/refactor-skills]
```

---

## Multi-Agent Development Workflow

### Scenario: 3 Agents Working in Parallel

**Issue 1:** Implement new AI system prompt  
**Issue 2:** Fix Rust linting rules  
**Issue 3:** Refactor skills structure  

### Agent Setup

```bash
# Agent 1 workspace
cd ../contextGarden-agent-1
# Workspace ready at: /home/kane/Workspaces/contextGarden-agent-1

# Agent 2 workspace (separate terminal)
cd ../contextGarden-issue-42
# Workspace ready at: /home/kane/Workspaces/contextGarden-issue-42

# Agent 3 workspace (separate terminal)
cd ../contextGarden-refactor
# Workspace ready at: /home/kane/Workspaces/contextGarden-refactor
```

### Each Agent Workflow

```bash
# Inside contextGarden-agent-1/
# 1. Make changes
vim agents/00-system-instruction.md

# 2. Commit locally
git add agents/00-system-instruction.md
git commit -m "feat: enhance system instruction with context awareness"

# 3. Push to remote
git push -u origin feature/agent-1

# Generate pull request (can be done in parallel!)
```

### Parallel Development Benefits

- **Agent 1** is making commits to `feature/agent-1` 
- **Agent 2** is simultaneously testing on `bugfix/issue-42`
- **Agent 3** is refactoring in `task/refactor-skills`
- **No blocking** on build/test cycles

---

## Advanced Patterns

### Pattern: Template-Based Worktree Creation

Create a script to automate worktree setup:

```bash
#!/bin/bash
# create-worktree.sh

REPO_BASE="/home/kane/Workspaces/contextGarden"
ISSUE_NUM=$1
ISSUE_TYPE=${2:-feature}  # feature, bugfix, task, etc.

if [ -z "$ISSUE_NUM" ]; then
    echo "Usage: ./create-worktree.sh <issue-num> [issue-type]"
    exit 1
fi

BRANCH_NAME="${ISSUE_TYPE}/issue-${ISSUE_NUM}"
WORKTREE_NAME="${REPO_BASE}-${ISSUE_NUM}"

git worktree add "$WORKTREE_NAME" -b "$BRANCH_NAME" origin/main

echo "✅ Worktree created: $WORKTREE_NAME"
echo "📌 Branch: $BRANCH_NAME"
echo "🚀 Ready: cd $WORKTREE_NAME"
```

**Usage:**
```bash
./create-worktree.sh 42 bugfix
# Creates: contextGarden-42 → bugfix/issue-42

./create-worktree.sh 99 feature
# Creates: contextGarden-99 → feature/issue-99
```

### Pattern: Parallel Build Testing

Test builds in parallel:

```bash
# Terminal 1: Build for agent-1
cd ../contextGarden-agent-1
npm run build  # or your build command

# Terminal 2: Build for agent-2 (simultaneously)
cd ../contextGarden-issue-42
npm test

# Terminal 3: Lint for agent-3
cd ../contextGarden-refactor
cargo clippy
```

---

## Integration with IDEs

### VS Code Multi-Root Workspace

Create `.code-workspace`:

```json
{
  "folders": [
    {
      "path": "/home/kane/Workspaces/contextGarden",
      "name": "🌿 Main"
    },
    {
      "path": "/home/kane/Workspaces/contextGarden-agent-1",
      "name": "🤖 Agent-1"
    },
    {
      "path": "/home/kane/Workspaces/contextGarden-issue-42",
      "name": "🐛 Issue-42"
    },
    {
      "path": "/home/kane/Workspaces/contextGarden-refactor",
      "name": "♻️ Refactor"
    }
  ],
  "settings": {
    "editor.wordWrap": "on"
  }
}
```

Open with:
```bash
code contextGarden.code-workspace
```

**Benefits:**
- All 4 projects visible in Explorer
- Search across all worktrees
- Shared settings and extensions
- Quick context switching via tabs

### Cursor IDE Setup

Create separate Cursor sessions:

```bash
# Terminal 1
cd ../contextGarden-agent-1
cursor .

# Terminal 2
cd ../contextGarden-issue-42
cursor .

# Terminal 3
cd ../contextGarden-refactor
cursor .
```

Each Cursor instance:
- Has independent project context
- Maintains separate AI chat history
- Can use different `.cursor/rules` per worktree

---

## Cleanup & Maintenance

### Remove Completed Worktree

```bash
# After merging PR for agent-1
git worktree remove ../contextGarden-agent-1

# Verify removal
git worktree list
```

### Clean Stale References

```bash
# Prune deleted branches
git fetch --prune

# List all pruned worktrees
git worktree list --pruned
```

### Force Remove Worktree

```bash
# If worktree is locked/corrupted
git worktree remove --force ../contextGarden-agent-1

# Or manually
rm -rf ../contextGarden-agent-1
git worktree prune
```

---

## Performance Considerations

### Disk Space

Each worktree requires space for:
- Full repository + `.git` directory
- Node modules / dependencies (if not shared)
- Build artifacts

**Estimation:**
```
Base repo:        ~500MB
Per worktree:     ~200-800MB (depending on node_modules)
3 worktrees:      ~1.5-2.5GB total
```

### Shared Dependencies (Optional)

Reduce disk usage with symlinked `node_modules`:

```bash
# In each worktree
ln -s ../contextGarden/node_modules ./

# Or use pnpm workspace for better sharing:
pnpm install --workspace-root
```

### Memory Impact

- **Main process:** ~100MB
- **Per IDE instance:** ~500MB-1GB
- **Build tools:** Varies by project

**Recommendation:** Minimum 8GB RAM for 3+ parallel worktrees with IDEs.

---

## Best Practices

### ✅ DO

- Create one worktree per **independent issue/agent**
- Use consistent naming: `contextGarden-{identifier}`
- Commit frequently in each worktree
- Push changes regularly to avoid merge conflicts
- Use descriptive branch names: `feature/`, `bugfix/`, `task/`

### ❌ DON'T

- Modify the same files across multiple worktrees (merge conflicts)
- Leave worktrees stale (sync regularly with `git pull`)
- Create worktrees from uncommitted changes
- Forget to remove completed worktrees (disk cleanup)

---

## Troubleshooting

### Lock File Errors

```
fatal: '/path/to/repo/.git/worktrees/...' is already locked
```

**Solution:**
```bash
# Force unlock
rm -f .git/worktrees/name/locked

# Or nuke problematic worktree
git worktree remove --force ../contextGarden-issue-42
```

### Branch Tracking Issues

```bash
# If worktree branch isn't tracking upstream
cd ../contextGarden-agent-1
git branch -u origin/feature/agent-1

# Verify tracking
git status
# Should show: "Your branch is up to date with 'origin/feature/agent-1'"
```

### Merge Conflicts After Long Parallel Work

```bash
# Before pushing, sync with main
git fetch origin
git rebase origin/main

# OR merge main into your branch
git merge origin/main

# Resolve conflicts, then:
git add .
git commit -m "Merge main: resolve conflicts"
git push
```

---

## Example: Full Multi-Agent Workflow

### Setup Phase (5 minutes)

```bash
# Main repo
cd contextGarden
git fetch origin
git checkout main

# Create 3 worktrees
git worktree add ../contextGarden-agent-1 -b feature/ai-prompts origin/main
git worktree add ../contextGarden-agent-2 -b bugfix/rust-lints origin/main
git worktree add ../contextGarden-agent-3 -b task/restructure-skills origin/main

# Open in VS Code multi-root
code contextGarden.code-workspace
```

### Development Phase (parallel)

**Terminal 1 - Agent 1:**
```bash
cd ../contextGarden-agent-1
# Edit agents/00-system-instruction.md
git add agents/
git commit -m "feat: enhanced system instructions"
git push -u origin feature/ai-prompts
```

**Terminal 2 - Agent 2:**
```bash
cd ../contextGarden-agent-2
# Edit skills/coding-guidelines/
git add skills/
git commit -m "fix: correct Rust lint rules"
git push -u origin bugfix/rust-lints
```

**Terminal 3 - Agent 3:**
```bash
cd ../contextGarden-agent-3
# Refactor skills/ structure
git add skills/
git commit -m "refactor: reorganize skills directory"
git push -u origin task/restructure-skills
```

### Cleanup Phase

```bash
# After PRs merged to main
git worktree remove ../contextGarden-agent-1
git worktree remove ../contextGarden-agent-2
git worktree remove ../contextGarden-agent-3

# Verify cleanup
git worktree list  # Should only show main
```

---

## Monitoring & Visualization

### Monitor Worktree Status

```bash
#!/bin/bash
# check-worktrees.sh

echo "📊 Worktree Status:"
git worktree list --porcelain | while read line; do
    worktree=$(echo "$line" | cut -d' ' -f1)
    branch=$(echo "$line" | cut -d' ' -f3 | tr -d 'detached-branch[]')
    
    if [ -d "$worktree" ]; then
        status="✅ Active"
    else
        status="⚠️ Missing"
    fi
    
    echo "$status | $branch | $(basename $worktree)"
done
```

### Git Worktree Dashboard

```bash
# See all worktrees with last commit
git worktree list | awk '{print $1}' | while read dir; do
    if [ -d "$dir" ]; then
        cd "$dir"
        branch=$(git rev-parse --abbrev-ref HEAD)
        commit=$(git log -1 --oneline)
        echo "📂 $(basename $dir)"
        echo "  ├─ Branch: $branch"
        echo "  └─ Last: $commit"
        cd - > /dev/null
    fi
done
```

---

## Integration with GitHub Copilot / Cursor AI

### Activate Copilot per Worktree

Each worktree can have:
- **Different `.copilot.json` settings** for project-specific rules
- **Independent chat context** in Cursor
- **Worktree-specific instructions** via `.instructions.md`

```bash
# contextGarden-agent-1/.instructions.md
# Focus on AI system prompts and agentic behavior

# contextGarden-agent-2/.instructions.md
# Focus on Rust code quality and lint rules
```

---

**Last Updated:** April 2026  
**Related:** [Error Protocol](../_meta/error-protocol.md) | [Project Rules](../project-rules/) | [Skills](../skills/)