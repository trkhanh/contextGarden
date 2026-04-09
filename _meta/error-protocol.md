# Error Protocol (3-Strike Rule)
> Systematic approach to handling errors with escalation

## Core Principle 
**If the same approach fails 3 times, escalate to the next level.**
Errors are not just problem to fix-they are signals about design appropriateness.

---
## The 3-Strike Rule
```
Strike 1: Fix at current layer
Strike 2: Question the approach, try alternative
Strike 3: Escalate to next layer up
```

### Why 3 Strikes?

| Strike | Purpose                                             |
| ------ | --------------------------------------------------- |
| 1      | Try obvious fix (maybe simple mistake)              |
| 2      | Try alternative approach (maybe wrong method)       |
| 3      | Question the design (maybe wrong approach entirely) |

--- 
## Strike Tracking
### In trace.md
```markdown
## Error Log
```