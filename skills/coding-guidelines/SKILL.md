---
---
---
**name**: coding-guidelines
**descriptions**: "Use when asking about Rust code style or best practices. Keywords: naming, formatting, comment, clippy, rustfmt, lint, code style, best practice, P.NAM, G.FMT, code review, naming convention, variable naming, function, naming, type naming"
**source**:  [trkhanh/rust-coding-guidelines-en: Rust Coding Guidelines](https://github.com/trkhanh/rust-coding-guidelines-en)
**user-invocable**: false

---
# Rust Coding Guidelines (50 Core Rules)
## Naming (Rust-Specific)
## Data types
## String
## Error Handling
## Memory
## Concurrency 
## Async
## Macros
## Deprecated → Better
## Quick Reference
```
Naming: snake_case (fn/var), CamelCase(Type), SCREAMING_CASE (const)
Format: rustfmt (just use it)
Docs: // for public items, //! for module docs
Lint: #![warn(clippy:all)]
```
Claude know Rust conventions well. These are the non-obvious Rust-specific rules.