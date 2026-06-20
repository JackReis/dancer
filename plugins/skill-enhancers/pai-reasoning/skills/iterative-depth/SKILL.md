---
name: iterative-depth
description: "Structured multi-angle exploration that runs 2-8 sequential passes through the same problem, each from a systematically different scientific lens, to surface requirements and edge cases invisible from any single angle. Grounded in 20 established techniques across cognitive science (Hermeneutic Circle, Triangulation), AI/ML (Self-Consistency, Ensemble Methods), requirements engineering (Viewpoint-Oriented RE), and design thinking (Six Thinking Hats, Causal Layered Analysis). Each pass outputs new criteria; passes stop when yields repeat. Best used at Extended+ effort — the default question should be why NOT to use it, not why to use it. A 4-lens pass routinely discovers 30-50% more criteria than direct analysis. NOT FOR scope/zoom analysis (use ApertureOscillation) or hypothesis-test cycles (use Science). USE WHEN iterative depth, explore deeper, multi-angle analysis, multiple perspectives, surface hidden requirements, all angles, blind spot check, deep dive before building, what am I missing, Extended or Deep effort, quick depth, fast angles."
---

# IterativeDepth

**Structured multi-angle exploration of the same problem to extract deeper understanding and richer criteria.**

Grounded in 20 established scientific techniques across cognitive science (Hermeneutic Circle, Triangulation), AI/ML (Self-Consistency, Ensemble Methods), requirements engineering (Viewpoint-Oriented RE), and design thinking (Six Thinking Hats, Causal Layered Analysis).

> Ported from PAI v5.0.0 (Daniel Miessler). Verbatim originals vendored at `resources/upstream-verbatim/pai-v5.0.0/skills/IterativeDepth/`.

## Core Concept

Instead of analyzing a problem once, run 2-8 structured passes through the same problem, each from a systematically different **lens**. Each pass surfaces requirements, edge cases, and criteria invisible from other angles. The combination yields criteria that no single-pass analysis could produce.

## Use / Win

**When to use:** Any time you have time budget beyond Standard tier and the task is important enough that getting the criteria right matters more than speed. This is the single most valuable thinking capability for the OBSERVE phase. If you're at Extended effort or above, you should be asking "why NOT use IterativeDepth?" rather than "why use it?"

Concrete triggers:
- **Extra time available** — Extended+ effort means you have the budget. Spend it on understanding the problem deeply before writing criteria, not on writing more code faster.
- **Deep analysis of what's actually being asked** — The user said X. But what do they actually need? What are they trying to accomplish? What would make them rate this 9-10? Single-pass reverse engineering catches the obvious. IterativeDepth catches the rest.
- **Different angles of approach** — Before committing to an approach, explore the problem from stakeholder, failure, temporal, experiential, and constraint-inversion angles. The right approach often only becomes obvious after seeing the problem from 3-4 directions.
- **Important or critical tasks** — When the user says "this is critical" or the task has high blast radius, the cost of missing a dimension is much higher than the cost of 2-5 extra minutes of analysis.
- **Tasks you've never done before** — Novel work has the highest density of hidden requirements. IterativeDepth is insurance against the things you don't know you don't know.

**What you win:**
- **Criteria that single-pass analysis cannot produce.** Each lens surfaces requirements invisible from other angles. A 4-lens pass routinely discovers 30-50% more criteria than direct analysis.
- **Blind spot elimination before they become mid-execution surprises.** Rework from missed requirements is 5-10x more expensive than the upfront analysis. IterativeDepth pays for itself by preventing restarts.
- **Approach clarity.** Seeing the problem from failure, stakeholder, and constraint-inversion angles often reveals that the obvious approach is wrong and a better path exists.
- **Confidence.** When criteria are built on multi-angle analysis, you can execute with conviction instead of discovering gaps halfway through.

**The default mental model should be:** At Extended+ effort, IterativeDepth is not optional enrichment — it's the standard way to understand what you're building before you build it.

## Workflow Routing

| Trigger | Action |
|---------|--------|
| "iterative depth", "explore deeper", "multi-angle" | Full exploration workflow |
| "quick depth", "fast angles" | Fast mode: 2 lenses |

## Quick Reference

- **8 Lenses** available, scaled by effort tier (2-8)
- **Each lens** is a structurally different exploration angle
- **Output** is new/refined criteria per pass
- **Integration** point: Deeper understanding through structured multi-angle analysis

**Full Documentation:**
- Scientific grounding: `ScientificFoundation.md`
- Lens definitions: `TheLenses.md`

## The 8 Lenses

Each lens is a structured perspective that forces exploration of a problem from a fundamentally different angle. Ordered from most concrete to most abstract.

### Lens 1: LITERAL (Surface Requirements)
**Question:** "What did they explicitly say? What are the concrete, stated requirements?"
**Focus:** Parse the exact words. Identify every stated requirement, constraint, preference. No interpretation — only what was said.

### Lens 2: STAKEHOLDER (Who Else Cares?)
**Question:** "Who are all the people, systems, and entities affected by this? What does each need?"
**Focus:** Identify every stakeholder beyond the requester. End users, maintainers, administrators, downstream systems, future developers.

### Lens 3: FAILURE (What Goes Wrong?)
**Question:** "What could fail? What would an adversary exploit? What are the edge cases?"
**Focus:** Assume the solution exists. Now break it. Error states, race conditions, security holes, data corruption, user confusion, performance under load.

### Lens 4: TEMPORAL (Past, Present, Future)
**Question:** "How does this change over time? What's the history? What happens in 6 months?"
**Focus:** Why does this problem exist now? What was tried before? What changes in the future that would break this solution? Migration paths, backwards compatibility, scale changes.

### Lens 5: EXPERIENTIAL (How Should It Feel?)
**Question:** "When this works perfectly, how does the user FEEL? What's the experience?"
**Focus:** Beyond functional correctness — the qualitative experience. Speed, elegance, surprise, delight, confidence, trust.

### Lens 6: CONSTRAINT INVERSION (What If?)
**Question:** "What if we removed all constraints? What if we added extreme ones?"
**Focus:** Remove assumed constraints — what would we build with infinite time/resources? Then add extreme constraints — what if it had to work offline, in 100ms, with zero dependencies?

### Lens 7: ANALOGICAL (What Patterns Apply?)
**Question:** "What similar problems have been solved before? What patterns from other domains apply?"
**Focus:** This problem isn't unique. What similar problems exist in other codebases, other industries, other fields? What patterns emerged there? What mistakes were made?

### Lens 8: META (Is This the Right Question?)
**Question:** "Are we solving the right problem? Is the framing itself correct?"
**Focus:** Step outside the problem entirely. Is the request a symptom of a deeper issue? Is there a reframing that dissolves the problem instead of solving it?

## Effort-Based Lens Selection

| Effort | Lenses | Which Ones | Time Budget |
|--------|--------|------------|-------------|
| Instant | 0 | Skip IterativeDepth entirely | 0s |
| Fast | 2 | Literal + Failure | <30s |
| Standard | 4 | Literal + Stakeholder + Failure + Experiential | <2min |
| Deep | 8 | All 8 lenses | <5min |

For specialized domains, override lens selection:
- **Security-focused task:** Prioritize Failure, Stakeholder, Temporal
- **UX-focused task:** Prioritize Experiential, Stakeholder, Literal
- **Architecture task:** Prioritize Temporal, Constraint Inversion, Analogical
- **Ambiguous request:** Prioritize Meta, Stakeholder, Literal

## Execution

### Step 1: Determine Depth
- Instant → SKIP
- Fast → N = 2 (Literal + Failure)
- Standard → N = 4 (Literal + Stakeholder + Failure + Experiential)
- Deep → N = 8 (All lenses)
- User specifies a number → N = that number (2-8)

### Step 2: Execute Passes
For each lens (1 through N), explore the problem exclusively through that lens. Each pass should surface genuinely NEW requirements, not restate previous findings.

### Step 3: Synthesize
1. **Deduplicate:** Remove criteria that are semantically identical across lenses
2. **Merge refinements:** If multiple lenses refined the same criterion, take the most specific version
3. **Prioritize:** Order criteria by how many lenses surfaced them (consensus = high priority)
4. **Format:** Output all new/refined criteria

### Step 4: Integrate
Return the enriched criteria to the calling context.

## Gotchas

- **2-8 lens passes, not infinite.** Diminishing returns after ~5 passes for most topics.
- **Each pass should surface genuinely NEW requirements, not restate previous findings.** If passes start repeating, stop early.
- **This is a BPE-fragile skill.** Monitor whether smarter models make it unnecessary. Quarterly test recommended.

## Examples

**Example 1: Surface hidden requirements**
```
User: "use iterative depth on this API redesign"
→ Pass 1: Functional requirements
→ Pass 2: Security implications
→ Pass 3: Performance constraints
→ Pass 4: Backward compatibility
→ Each pass surfaces new requirements missed by previous
```

## Customization (Optional)

Users may place overrides in a skill-customizations directory. If a customization directory exists for this skill, load and apply any preferences found there. This is an optional pattern — proceed with defaults if no customizations exist.
