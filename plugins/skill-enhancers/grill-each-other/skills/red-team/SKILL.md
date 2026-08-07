---
name: red-team
description: Military-grade adversarial analysis that deploys 32 parallel expert agents (engineers, architects, pentesters, interns) to stress-test ideas, strategies, and plans — not systems or infrastructure. Two workflows: ParallelAnalysis (5-phase: decompose into 24 atomic claims → 32-agent parallel attack → synthesis → steelman → counter-argument, each 8 points) and AdversarialValidation (competing proposals synthesized into best solution). Findings ranked by severity; goal is to strengthen, not destroy — weaknesses delivered with remediation paths. Collaborates with FirstPrinciples (decompose assumptions before attacking) and Council (Council debates to find paths; RedTeam attacks whatever survives). NOT FOR AI instruction set auditing (use bitter-pill-engineering). NOT FOR network/system vulnerability testing (use a security assessment skill). USE WHEN red team, attack idea, counterarguments, critique, stress test, devil's advocate, find weaknesses, break this, poke holes, what could go wrong, strongest objection, adversarial validation, battle of bots.
---

# Red Team

Military-grade adversarial analysis using parallel agent deployment. Breaks arguments into atomic components, attacks from 32 different expert perspectives simultaneously, synthesizes findings, and produces the ultimate counter-argument.

## Key Philosophy

**The goal is NOT destruction** — it's finding the fundamental flaw in an argument's logic: the assumption that, if challenged, causes the entire structure to collapse.

The most powerful critique is usually **ONE core issue**:
- A hidden assumption that's actually false
- A logical step that doesn't follow
- A category error (treating X like Y)
- An ignored precedent that directly contradicts

## Workflow Routing

| Trigger | Workflow |
|---------|----------|
| Red team analysis (stress-test existing content) | `Workflows/ParallelAnalysis.md` |
| Adversarial validation (produce new content via competition) | `Workflows/AdversarialValidation.md` |

## Quick Reference

| Workflow | Purpose | Output |
|----------|---------|--------|
| **ParallelAnalysis** | Stress-test existing content | Steelman + Counter-argument (8 points each) |
| **AdversarialValidation** | Produce new content via competition | Synthesized solution from competing proposals |

**The Five-Phase Protocol (ParallelAnalysis):**
1. **Decomposition** — Break into 24 atomic claims
2. **Parallel Analysis** — 32 agents examine strengths AND weaknesses
3. **Synthesis** — Identify convergent insights
4. **Steelman** — Strongest version of the argument
5. **Counter-Argument** — Strongest rebuttal

## The 32 Agent Types

| Type | Count | Focus |
|------|-------|-------|
| **Engineers** | 8 | Technical and logical rigor |
| **Architects** | 8 | Structural and systemic issues |
| **Pentesters** | 8 | Adversarial thinking |
| **Interns** | 8 | Fresh perspectives |

Scale "32 agents" to Jack's parallel `Agent(subagent_type="general-purpose")` dispatch reality — compose the agent roster with topic-specific traits and launch in a single batched message.

## Integration

**Use BEFORE RedTeam:**
- **Research** — Gather context, find precedents

**Use DURING RedTeam:**
- **FirstPrinciples** — Decompose assumptions before attacking (Phase 1 enhancement + Phase 5 challenge)

**Use AFTER RedTeam:**
- **Council** — Multi-perspective debate to find the best path after adversarial stress-test
- **ExtractWisdom** — Find highest-signal critiques

## Anti-Fragile vs Fragile

**Keep (anti-fragile):** Verification harnesses, ISC, data pipelines, specific DO/DON'T examples, tool preferences, routing rules.

**Cut (fragile):** CoT orchestrators, format parsers, retry cascades, numeric personality scales, abstract value statements.

## Gotchas

- **RedTeam is for attacking IDEAS, not systems.** This skill finds flaws in arguments, strategies, and plans — not network vulnerabilities.
- **32 adversarial agents generate volume — not all findings are equal.** Rank by severity, discard noise.
- **The goal is to strengthen, not destroy.** Present weaknesses constructively with remediation paths.
- **Steelman before counter.** The counter-argument must defeat the strongest version of the argument, not a weaker strawman.

---

**Attribution:** Mechanics adapted from PAI v5.0.0 RedTeam skill (Daniel Miessler, MIT-licensed). De-PAI'd for Jack's multi-agent fleet — ComposeAgent (bun runtime) replaced with `Agent(subagent_type="general-purpose")` dispatch; voice notification curl removed; execution log dropped.
