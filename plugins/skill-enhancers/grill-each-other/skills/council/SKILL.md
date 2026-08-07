---
name: council
description: Multi-agent collaborative debate that produces visible round-by-round transcripts with genuine intellectual friction. All council members are custom-composed via Agent(subagent_type="general-purpose") dispatch with domain expertise, unique voice, and personality tailored to the specific topic. Two workflows: DEBATE (3 rounds, full transcript + synthesis, parallel execution within rounds) and QUICK (1 round, fast perspective check). Council is collaborative-adversarial (debate to find best path); for pure adversarial attack, use red-team. NOT FOR multi-agent collaboration design (use grill-me-agents). USE WHEN council, debate, multiple perspectives, weigh options, deliberate, get different views, multi-agent discussion, what would experts say, is there consensus, pros and cons from multiple angles.
---

# Council

Multi-agent debate system where custom-composed agents discuss topics in rounds, respond to each other's points, and surface insights through intellectual friction.

## Core Concept

**Council is collaborative-adversarial** — agents debate to find the best path, not to destroy ideas. The visible, round-by-round transcript makes the intellectual journey inspectable: you can see where agents changed their minds, where they held firm, and where genuine new insight emerged.

**Council vs. RedTeam:** Council is collaborative-adversarial (debate to find best path); RedTeam is purely adversarial (attack the idea). Council produces visible conversation transcripts; RedTeam produces steelman + counter-argument.

## Custom Agents Only

**ALL council members MUST be custom-composed agents dispatched via `Agent(subagent_type="general-purpose")`.** NEVER use built-in agent types (Architect, Designer, Engineer, etc.).

Built-in types are generic and topic-ignorant. Council debates require agents with:
- Domain expertise tailored to the specific debate topic
- Unique voices and personalities
- Distinct analytical approaches that create genuine friction

### Default Perspective Slots

When the user doesn't specify council members, compose 4 agents covering these perspective types (but with topic-specific traits):

| Slot | Purpose | Example Trait Combos |
|------|---------|---------------------|
| **Builder** | Has built things in this domain | `technical,enthusiastic,systematic` |
| **Skeptic** | Challenges assumptions, finds flaws | `[domain],skeptical,meticulous` |
| **Pragmatist** | Implementation reality, trade-offs | `technical,pragmatic,analytical` |
| **Analyst** | Data, precedent, external evidence | `research,analytical,comparative` |

## Workflow Routing

| Trigger | Workflow |
|---------|----------|
| Full structured debate (3 rounds, visible transcript) | `Workflows/Debate.md` |
| Quick consensus check (1 round, fast) | `Workflows/Quick.md` |
| Pure adversarial analysis | `red-team` |

## Quick Reference

| Workflow | Purpose | Rounds | Output |
|----------|---------|--------|--------|
| **DEBATE** | Full structured discussion | 3 | Complete transcript + synthesis |
| **QUICK** | Fast perspective check | 1 | Initial positions only |

## Core Philosophy

**Origin:** Best decisions emerge from diverse perspectives challenging each other. Not just collecting opinions — genuine intellectual friction where domain-specific experts respond to each other's actual points.

**Speed:** Parallel execution within rounds, sequential between rounds. A 3-round debate of 4 agents = 12 agent calls but only 3 sequential waits. Complete in 40-90 seconds.

## Examples

```
"Council: Should we use WebSockets or SSE?"
→ Compose 4 custom agents with relevant traits (real-time, frontend, ops, research)
→ DEBATE workflow → 3-round transcript

"Quick council check: Is this API design reasonable?"
→ Compose 4 custom agents with API-relevant traits
→ QUICK workflow → Fast perspectives

"Council: Is AI overhyped?"
→ Compose agents: AI builder, security skeptic, pragmatic engineer, evidence analyst
→ DEBATE workflow → 3-round transcript
```

## Integration

**Depends on:**
- **Agent dispatch** (`Agent(subagent_type="general-purpose")`) for creating all council members

**Works well with:**
- **red-team** — Pure adversarial attack after collaborative discussion
- **Research** — Gather context before convening the council
- **dialectic-vocabulary** — The scholastic substrate for structured disputation

## Gotchas

- **Council uses custom agents — NEVER built-in agent types.** Always compose with topic-specific traits.
- **Debates need genuine disagreement to be valuable.** If all agents agree, the topic may not warrant Council.
- **More agents ≠ better debate.** 4-6 well-composed agents outperform 12 generic ones.
- **The visible transcript is the deliverable.** The insights are in the responses and how they change across rounds, not just in initial positions.

---

**Attribution:** Mechanics adapted from PAI v5.0.0 Council skill (Daniel Miessler, MIT-licensed). De-PAI'd for Jack's multi-agent fleet — ComposeAgent (bun runtime) replaced with `Agent(subagent_type="general-purpose")` dispatch; voice notification curl removed; execution log dropped.
