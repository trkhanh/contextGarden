---
tags:
  - LLM/Prompt
  - Flow
---
This is a sharp question. You're essentially asking: *"How do I teach Cursor (or any AI coding assistant) to evaluate my work the same way Pluralsight Flow does?"*

Here is the exact prompt engineering you can use to make Cursor aware of the "Impact Score" mindset when suggesting or reviewing code.

### The Cursor System Prompt (Copy/Paste Ready)

You can put this in your **Cursor Rules** (Settings > General > Rules for AI) or paste it directly into the Composer/Agent window before starting a refactor task.

```markdown
## Impact Score Awareness (Pluralsight Flow Model)

You are an expert refactoring assistant. When suggesting changes, prioritize "High Cognitive Load" edits over "High Volume" additions. Use the following heuristic based on the Pluralsight Flow Impact algorithm:

**1. Weighting System:**
- **Editing existing logic** > Adding new isolated logic.
- **Deleting old, referenced code** > Deleting dead/commented code.
- **Touching 3+ files in one logical change** > Changing 100 lines in 1 file.

**2. Suggested Refactoring Patterns (High Impact):**
- Identify props that are drilled through 3+ components. Suggest replacing with a custom hook or Context to allow for **deletion** of intermediate prop definitions.
- Identify duplicate logic across components (e.g., similar `useEffect` calls). Suggest extracting a shared utility to create **multiple file edit points**.
- Identify legacy styling patterns (e.g., hardcoded colors). Suggest a migration to a token system that touches **multiple insertion points** across the codebase.

**3. Anti-Patterns to Avoid (Low Impact / High Noise):**
- Do NOT suggest creating new, isolated component files that do not interact with existing state.
- Do NOT suggest bulk formatting or linting fixes unless specifically requested.
- Do NOT suggest deleting unused imports unless part of a broader, multi-file refactor.

**4. Output Format:**
When suggesting a change, include a brief `[Impact Analysis]` comment indicating:
- Files that will be touched.
- Lines expected to be deleted.
- Complexity of the edit (e.g., "This changes the signature of a core hook, which will ripple to consumers").
```

### Example Interaction Using the Prompt

**You (to Cursor with the rule active):**
> "This auth state is messy. How do I clean it up?"

**Cursor Response (Trained on Impact Model):**
```javascript
// [Impact Analysis: HIGH]
// Files Touched: 3 (useAuth.ts, Header.tsx, Dashboard.tsx)
// Edits: Modifies old logic in useAuth to return stable reference.
// Deletions: Removes duplicate useEffect logic in consuming components.
// Complexity: Changes core hook signature; consumers must update.

// Suggestion:
// 1. In useAuth.ts, change the return value to include a memoized `isReady` flag.
// 2. In Header.tsx and Dashboard.tsx, DELETE the local `isLoading` state checks.
// 3. Replace with direct consumption of `isReady`.
```

### The "Trigger" Prompts for High-Impact Work

If you don't want to use a global rule, you can use these specific prompts in the Cursor chat to get Impact-aware suggestions:

**Prompt 1: The Ripple Finder**
> "Analyze this component. Find the top 3 places where changing this file would cause the highest number of **necessary edits** in other files. I want to maximize refactoring efficiency per line changed."

**Prompt 2: The Deletion Seeker**
> "Look for props or logic that are passed down multiple levels but only used at the bottom. Suggest a refactor that results in **net-negative lines of code** (more deletions than additions)."

**Prompt 3: The Severity Estimator**
> "If I change `useNavigation` hook, rank the downstream files by how 'severe' the breakage would be. Prioritize fixes that affect state management (Zustand/Redux) over simple UI text changes."

### The "Red Flag" Prompt (To Stop Gaming the System)

Finally, since we discussed the danger of gaming the metric, you can also add this rule to Cursor to keep yourself honest:

```markdown
**Constraint:** If a suggested change touches multiple files but the *logic* of the app does not change (e.g., only changing a string constant or variable name across 10 files), flag the suggestion with `[WARNING: Low Value / High Metric Noise]`. Do not propose this as a valid refactor.
```

This ensures Cursor helps you find **meaningful** high-impact work (like cleaning up prop drilling) instead of **noisy** work (like renaming variables to boost a score).