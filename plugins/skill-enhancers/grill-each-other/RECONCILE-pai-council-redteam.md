# Reconcile: PAI Council + RedTeam into grill-each-other

## Objective

Decide, per PAI mechanic, whether Council and RedTeam land as NEW skills or ENHANCEMENTS to existing grill-each-other skills. Record the decision with rationale.

## Existing grill-each-other skill inventory

| Skill | Purpose |
|-------|---------|
| `grill-me` | Solo adversarial self-stress-test of a claim or design |
| `grill-me-agents` | Multi-agent debate to design/stress-test agent collaboration (13 branches) |
| `grill-me-with-agents` | Code-aware variant of grill-me-agents (existing stack audit) |
| `peer-grill` | Strict file-only multi-agent reconciliation (claims → grill-log → RATIFY) |
| `peer-grill-with-agents` | Multi-agent audit of existing agent stack, then reconcile |
| `fleet-ratify` | N-agent formal capstone attestation of an artifact |
| `dialectic-vocabulary` | Scholastic + Greek vocabulary for structured disputation |
| `permutation` | Visual topology generation (Mermaid/Excalidraw) from claims |
| `agent-show-and-tell` | Fleet-wide visibility report from each agent |

## Novel PAI mechanics — overlap analysis

### Council novel mechanics

| Mechanic | Existing coverage? | Decision |
|----------|-------------------|----------|
| **Visible round-by-round debate transcript** (3 rounds: positions → challenges → synthesis) | grill-me-agents debates but outputs design, not a visible debate transcript; peer-grill produces a grill-log.md but it's a reconciliation protocol, not a multi-agent debate | **NEW skill: `council`** — the visible 3-round debate transcript is genuinely absent from the existing pack |
| **Custom-composed agents with topic-specific traits** (ComposeAgent) | grill-me-agents uses `Agent(subagent_type=...)` dispatch but not the visible-debate format | Covered by council's new skill (same mechanism, different output format) |
| **DEBATE vs QUICK workflows** | Not present | **NEW skill: `council`** — fast sanity check vs. full structured debate |
| **Collaboration with RedTeam** (RedTeam attacks whatever survives debate) | Not present | council defers to `red-team` |

### RedTeam novel mechanics

| Mechanic | Existing coverage? | Decision |
|----------|-------------------|----------|
| **5-phase protocol** (Decompose → 32-agent parallel attack → Synthesis → Steelman → Counter-argument) | grill-me is solo; peer-grill is file-based reconciliation; neither has 32-agent fan-out | **NEW skill: `red-team`** |
| **Steelman + Counter-argument output** (8 points each, 12-16 words each) | Not present in any existing skill | **NEW skill: `red-team`** |
| **Severity ranking + strengthen-not-destroy** | dialectic-vocabulary covers refutation but not the military-grade adversarial protocol | **NEW skill: `red-team`** |
| **Cross-link to dialectic-vocabulary** | Already cross-linked in existing skills | Cross-link in red-team SKILL.md |
| **32-agent parallel deployment** (8 engineers, 8 architects, 8 pentesters, 8 interns) | Not present | **NEW skill: `red-team`** — scale to Jack's parallel Agent dispatch reality |

## Decisions

1. **RedTeam → NEW skill `red-team`** in `grill-each-other/skills/red-team/`. The 5-phase steelman+counter protocol is genuinely absent from the existing pack.
2. **Council → NEW skill `council`** in `grill-each-other/skills/council/`. The visible 3-round debate transcript format is distinct from grill-me-agents (which targets agent-stack design, not topic debate).
3. Both skills cross-link `dialectic-vocabulary` as the shared scholastic substrate.
4. Both skills replace `ComposeAgent.ts` / `bun run` with `Agent(subagent_type="general-purpose")` dispatch language, adapted to Jack's fleet reality.
5. Both skills defer to each other: council's RedTeam integration → `red-team`; red-team's adversarial analysis → `council` for collaborative debate after attack.

## Verification

- Every novel mechanic is covered by either a new skill or an existing skill with documented rationale.
- The decision note lists every novel mechanic with its new-vs-enhance-vs-covered verdict.
