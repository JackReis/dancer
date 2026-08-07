---
name: iterative-depth
description: Use when you need deeper understanding before planning or building. Triggers include "iterative depth", "explore deeper", "multi-angle analysis", "multiple perspectives", "surface hidden requirements", "blind spot check", "deep dive", or Extended/Deep effort. Runs 2-8 sequential passes through the same problem from structurally different lenses to extract ISC criteria invisible from any single angle. Stop when yields repeat. Not for scope/zoom analysis (use aperture-oscillation) or hypothesis-test cycles (use science).
---

# Iterative Depth

**Structured multi-angle exploration of the same problem to extract deeper understanding and richer ISC criteria.**

Grounded in 20 established scientific techniques across cognitive science (Hermeneutic Circle, Triangulation), AI/ML (Self-Consistency, Ensemble Methods), requirements engineering (Viewpoint-Oriented RE), and design thinking (Six Thinking Hats, Causal Layered Analysis).

## Core Concept

Instead of analyzing a problem once, run 2-8 structured passes through the same problem, each from a systematically different **lens**. Each pass surfaces requirements, edge cases, and criteria invisible from other angles. The combination yields ISC criteria that no single-pass analysis could produce.

## When to Use

Any time you have budget beyond Standard effort and the task is important enough that getting the ISC right matters more than speed. At Extended+ effort, the default question should be "why NOT use iterative depth?" rather than "why use it?"

Concrete triggers:
- **Extra time available** — Extended+ effort means you have the budget. Spend it understanding the problem before writing ISC.
- **Deep analysis of what's actually being asked** — The user said X. What do they actually need? What would make them rate this 9-10?
- **Different angles of approach** — Before committing, explore stakeholder, failure, temporal, experiential, and constraint-inversion angles.
- **Important or critical tasks** — When the user says "this is critical" or the task has high blast radius.
- **Tasks you've never done before** — Novel work has the highest density of hidden requirements.

## What You Win

- ISC criteria that single-pass analysis cannot produce.
- Blind spots eliminated before they become mid-execution surprises.
- Approach clarity — the obvious path is often wrong until you see it from 3-4 angles.
- Confidence grounded in multi-angle analysis.

## The 8 Lenses

| # | Lens | Question | ISC Output |
|---|---|---|---|
| 1 | **Literal** | What did they explicitly say? | Every stated requirement |
| 2 | **Stakeholder** | Who else cares? What do they need? | Unstated stakeholder requirements |
| 3 | **Failure** | What could fail or be exploited? | Anti-criteria and defensive criteria |
| 4 | **Temporal** | How does this change over time? | Durability, migration, future-proofing |
| 5 | **Experiential** | How should it feel when it works perfectly? | Quality-of-experience criteria |
| 6 | **Constraint Inversion** | What constraints are we assuming? | What's truly essential |
| 7 | **Analogical** | What similar problems have been solved? | Criteria from proven patterns |
| 8 | **Meta** | Are we solving the right problem? | Reframing or expanded problem definition |

Full definitions and prompt variations: `TheLenses.md`.

## Workflow

1. **Select SLA** based on effort budget:
   - **Fast:** 2 lenses (Literal + Failure)
   - **Standard:** 4 lenses (Literal + Stakeholder + Failure + Experiential)
   - **Deep:** 8 lenses (all)
2. **Run each lens as a separate pass.** Treat each pass as a fresh analysis of the same problem from that angle only.
3. **Capture new ISC criteria** after each pass. Number them continuously (do not renumber existing criteria).
4. **Stop when yields repeat.** If a pass produces no materially new criteria, you are done.
5. **Synthesize** into the plan's Criteria section, marking which lens surfaced each criterion.

For Deep SLAs, the 8 lenses can be parallelized as separate background analyses and then synthesized.

## Integration with Fleet Tools

- Use `grill-each-other:dialectic-vocabulary` to mark claims and anti-claims discovered during the Failure lens.
- Use `Agent(subagent_type="explore")` or other fleet agents to run lenses in parallel when appropriate.

## Gotchas

- **2-8 passes, not infinite.** Diminishing returns after ~5 passes for most topics.
- **Each pass must surface genuinely NEW requirements.** If passes start repeating, stop early.
- **This is BPE-fragile.** Monitor whether smarter models make it unnecessary. Quarterly test recommended.
- **Not a substitute for execution.** IterativeDepth produces criteria; it does not build the solution.

## Example

User: "Use iterative depth on this API redesign before we write the implementation plan."

→ Pass 1 (Literal): list every explicit requirement.
→ Pass 2 (Stakeholder): identify downstream consumers and their unstated needs.
→ Pass 3 (Failure): enumerate failure modes and anti-criteria.
→ Pass 4 (Temporal): identify migration and versioning requirements.
→ Synthesize into Criteria section; proceed to implementation planning.

## References

- Scientific grounding: `ScientificFoundation.md`
- Lens definitions + SLA tables: `TheLenses.md`
