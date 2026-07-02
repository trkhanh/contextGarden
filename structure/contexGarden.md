# Context Garden
```
.context/
├── .index.md                          # LLM Router (NEW)
│
├── agents/                            # (RENAMED from commands)
│   ├── core/                          # Utilities
│   ├── context-focused.md
│   ├── elevate.md
│   ├── think.md
│   └── knowledge-transfer.md
│
├── memory/                            # (RENAMED from knowledge) - Static facts
│   ├── architecture.md
│   ├── domain-logic.md                # "What is a Settlement Leg?"
│   └── dependencies.md
│
├── rules/                             # Active constraints
│   ├── code-style.md
│   ├── testing.md
│   └── impact-score.md                # (Your new Impact rule from previous chat)
│
├── defects/                           # Historical (Git-like log)
│   ├── 001-refinance-settlement.md
│   ├── 002-entity-visibility.md
│   └── 003-multi-currency-check.md
│
├── goals/                             # Strategic (OKRs for code)
│   ├── anti-pattern-mitigation.md
│   └── elevate-ambassador.md
│
├── prompts/                           # Library of copy-paste prompts
│   └── react-refactor-prompts.md
│
├── techdebt/                          # Active issues
│   └── type-safety-audit.md
│
└── sessions/                          # (NEW) - Temporal working memory
    └── 2026-04-09-refactoring-auth.md
```