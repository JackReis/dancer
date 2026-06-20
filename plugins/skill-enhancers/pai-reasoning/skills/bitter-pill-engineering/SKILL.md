---
name: bitter-pill-engineering
description: "Audits any AI instruction set for over-prompting using the core test: would a smarter model make this rule unnecessary? Applies Five Questions to every rule — Does the model already do this? Contradiction? Redundant? One-off fix? Vague? — then classifies each as CUT / RESOLVE / MERGE / EVALUATE / SHARPEN / MOVE / KEEP. Two workflows: Audit (full system — reads all force-loaded files, reports token savings estimate) and QuickCheck (single file, fast keep/cut/sharpen verdict). Outputs categorized report with estimated line and token savings. Core principle: less scaffolding = better output — every unnecessary rule competes for attention and degrades the rules that matter. Anti-fragile rules to KEEP: verification harnesses, ISC, data pipelines, specific DO/DON'T examples, tool preferences, routing rules. Fragile rules to CUT: CoT orchestrators, format parsers, retry cascades, numeric personality scales, abstract value statements. Cross-links grill-each-other:dialectic-vocabulary (over-prompting audit = anti-theatre / examined-claim doctrine). NOT FOR general code simplification or refactoring. NOT FOR attacking logical or strategic flaws in ideas (use red-team for that). USE WHEN BPE, bitter pill, audit setup, over-prompting, trim instructions, audit rules, dead weight, redundant rules, simplify setup, instruction audit, prompt hygiene, check these rules, clean up CLAUDE.md."
---

# BitterPillEngineering

Audit any AI instruction set for over-prompting. Based on the principle that **less scaffolding = better output** — every unnecessary rule competes for attention and degrades the rules that matter.

> Ported from PAI v5.0.0 (Daniel Miessler). Verbatim originals vendored at `resources/upstream-verbatim/pai-v5.0.0/skills/BitterPillEngineering/`.

> **Cross-link:** This skill aligns with `grill-each-other:dialectic-vocabulary` — the over-prompting audit is the anti-theatre / examined-claim doctrine applied to instruction sets. An unexamined rule does not exist.

The core test: *"Would a smarter model make this unnecessary?"* If yes, it's scaffolding, not architecture.

## Workflow Routing

| Workflow | Trigger | Description |
|----------|---------|-------------|
| **Audit** | "audit setup", "full audit", "check all rules" | Full system — reads all force-loaded files, reports token savings estimate |
| **QuickCheck** | "quick check", "check this file", "check these rules" | Single file, fast keep/cut/sharpen verdict |

## Examples

**Example 1: Full system audit**
```
User: "Run BPE on my setup"
→ Invokes Audit workflow
→ Reads all force-loaded files
→ Evaluates each rule against the Five Questions
→ Returns categorized report with estimated token savings
```

**Example 2: Check a single file**
```
User: "Quick check this CLAUDE.md"
→ Invokes QuickCheck workflow
→ Reads the target file
→ Returns concise keep/cut/sharpen verdict
```

**Example 3: Post-cleanup validation**
```
User: "I trimmed my rules, check if anything's still redundant"
→ Invokes Audit workflow
→ Compares remaining rules against model defaults
→ Flags any surviving dead weight
```

## The Five Questions

For every rule, instruction, or preference found, evaluate:

1. **Default behavior?** Does the model already do this without being told?
2. **Contradiction?** Does this conflict with another rule in the same or different file?
3. **Redundancy?** Is this already covered by a different rule or file?
4. **One-off fix?** Was this added to fix one specific bad output rather than improve outputs generally?
5. **Vague?** Would the model interpret this differently every time? (e.g., "be more natural", numeric personality scales)

## Classification

| Category | Action |
|----------|--------|
| Restates default behavior | **CUT** — the model already does this |
| Contradicts another rule | **RESOLVE** — pick one, cut the other |
| Duplicates another rule | **MERGE** — one location, one statement |
| One-off fix for past mistake | **EVALUATE** — still relevant or already learned? |
| Vague / unquantifiable | **SHARPEN** — add specific DO/DON'T examples, or cut |
| Loaded but rarely actionable | **MOVE to on-demand** — load via context routing when needed |
| Specific, actionable, non-default | **KEEP** — this is what good instructions look like |

## Anti-Fragile vs Fragile

**Keep (anti-fragile):** Verification harnesses, ISC, data pipelines, specific DO/DON'T examples, tool preferences, routing rules.

**Cut (fragile):** CoT orchestrators, format parsers, retry cascades, numeric personality scales, abstract value statements, process descriptions that aren't followed.

## Output Format

```
## BitterPillEngineering Audit

**Scope:** [what was audited]
**Files read:** [count]
**Rules evaluated:** [count]

### CUT (restating defaults)
- [rule] — [reason]

### RESOLVE (contradictions)
- [rule A] vs [rule B] — [which to keep and why]

### MERGE (redundancies)
- [locations] — [merge into where]

### EVALUATE (one-off fixes)
- [rule] — [still needed? verdict]

### SHARPEN or CUT (vague)
- [rule] — [sharpen how, or cut why]

### MOVE to on-demand
- [content] — [how often it's actually needed]

### KEEP (carrying weight)
- [rule] — [why it matters]

**Estimated savings:** [lines] lines, ~[tokens] tokens
```

## Gotchas

- Model built-in system prompts change across versions — what was "default behavior" 3 months ago may not be now. When in doubt, test rather than assume.
- Rules that seem redundant with defaults may have been added because the model was inconsistent about following the default. Check failure history before cutting.
- "One-off fix" rules sometimes prevent recurring failures. Check if the failure pattern is truly gone before removing.
- If using settings.json with `loadAtStartup` and `postCompactRestore.fullFiles`, keep them in sync — removing a file from one requires checking the other.

## Customization (Optional)

Users may place overrides in a skill-customizations directory. If a customization directory exists for this skill, load and apply any preferences found there. This is an optional pattern — proceed with defaults if no customizations exist.
