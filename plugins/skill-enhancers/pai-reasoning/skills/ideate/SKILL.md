---
name: ideate
description: Evolutionary ideation engine — loop-controlled multi-cycle idea generation through 9 phases (CONSUME, DREAM at noise=0.9, DAYDREAM at noise=0.5, CONTAMINE at noise=0.1, STEAL cross-domain borrowing, MATE recombination via Fisher-Yates shuffle, TEST fitness scoring, EVOLVE selection, META-LEARN Lamarckian strategy adjustment). Loop Controller drives adaptive continue/pivot/stop logic with mid-cycle quality checkpoints. Produces ranked novel solution candidates with full provenance and fitness landscape. NOT FOR quick single-pass brainstorming (use be-creative). NOT FOR ideation that needs scope oscillation (use aperture-oscillation). USE WHEN ideate, novel ideas, generate ideas, ideation engine, evolve ideas, dream up solutions, innovate, breakthrough ideas, idea evolution, creative solutions to hard problems, multi-cycle creativity, need genuinely new approaches.
---

# Ideate — The Cognitive Progress Engine

A loop-controlled evolutionary creativity engine that mirrors human cognitive processes to generate genuinely novel ideas. **This is NOT be-creative** — be-creative is a single-pass diversity tool. Ideate is an evolutionary *system*: multiple cycles of consuming, dreaming, stealing, breeding, and testing ideas, driven by a first-class Loop Controller and a Lamarckian Meta-Learner.

## The Core Insight

Human creativity reduces to 5 irreducible functions:

| Function | What It Does | Human Analog |
|----------|--------------|--------------|
| **INGEST** | Gather diverse raw material | Reading, conversations, experiences |
| **PERTURB** | Recombine inputs with controlled noise | Dreaming, daydreaming, shower thoughts |
| **CROSS-POLLINATE** | Map patterns from foreign domains | "Stealing" ideas from unrelated fields |
| **SELECT** | Score against fitness function | Critical thinking, peer review, testing |
| **ITERATE** | Feed survivors back as inputs | Sleep cycles, weeks of study, years of work |

The 9 workflow phases expand these into a richer human-legible system.

## The 9 Phases (Summary)

| # | Phase | Noise | What it does | Cognitive Agent |
|---|-------|-------|--------------|---------|
| 1 | **CONSUME** | — | Multi-domain research, atomic idea extraction | The Glutton |
| 2 | **DREAM** | 0.9 | Free-association on random input subsets, no problem awareness | The Dreamer |
| 3 | **DAYDREAM** | 0.5 | Tangential wandering with the problem held loosely | The Wanderer |
| 4 | **CONTEMPLATE** | 0.1 | Structured analysis via 4 lenses (mandatory; checkpoint A gates) | The Sage |
| 5 | **STEAL** | — | Cross-domain pattern borrowing via weighted random domain lottery | The Thief |
| 6 | **MATE** | — | Genetic recombination via Fisher-Yates shuffle + 8 mutation operations | The Matchmaker |
| 7 | **TEST** | — | Multi-judge scoring on Feasibility/Novelty/Impact/Elegance (checkpoint B gates) | The Judge |
| 8 | **EVOLVE** | — | Selection: kill bottom 50%, elite top 10%, mutate the rest, immigrant injection | The Curator |
| 9 | **META-LEARN** | — | Lamarckian strategy adjustment + next-cycle question generation | The Scientist |

Post-loop: The Historian runs the Insight Extractor for cross-cycle pattern analysis.

## Workflow Routing

| User says... | Workflow |
|--------------|----------|
| "ideate", "novel ideas for X", "evolve ideas for X", default | `Workflows/FullCycle.md` |
| "quick novelty for X", "fast brainstorm with scoring" | `Workflows/QuickCycle.md` |
| "dream on X", "free-associate these inputs", "wild recombinations" | `Workflows/Dream.md` |
| "steal ideas from biology for X", "cross-pollinate from Y" | `Workflows/Steal.md` |
| "breed these ideas", "recombine X and Y" | `Workflows/Mate.md` |
| "score these candidates", "test these ideas against fitness" | `Workflows/Test.md` |

## The Loop Controller

Owns inter-cycle state and makes continue/pivot/stop decisions after each cycle's META-LEARN phase. State tracked:

```json
{
  "cycle_count": 0,
  "max_cycles": null,
  "budget_seconds_remaining": 600,
  "fitness_history": [{"cycle": 1, "avg_score": 52.3, "top_score": 68.1, "diversity_index": 0.91}],
  "stagnation_counter": 0,
  "strategy_version": 1,
  "strategy_adjustments": {},
  "loop_decision_log": []
}
```

**Loop Gate logic:**
```
IF budget_seconds_remaining <= 0:        STOP (budget exhausted)
ELIF stagnation_counter >= 3:
    IF strategy_pivots_remaining > 0:    PIVOT (shift domains/noise/agents)
    ELSE:                                STOP (exhausted strategies)
ELIF diversity_index < 0.3:              PIVOT (collapse — inject immigrants)
ELIF top_score >= target_score:          STOP (target reached)
ELSE:                                    CONTINUE
```

## Structural Randomness Engine

Uses **structural randomness** at the data level instead of LLM temperature:

- **Input subsetting** (DREAM): Fisher-Yates shuffle picks each agent's input subset
- **Domain lottery** (STEAL): weighted random sampling from the candidate domain pool
- **Pairing shuffle** (MATE): Fisher-Yates pairs adjacent items; 20% slots forced cross-phase
- **Mutation dice** (EVOLVE): roll an 8-sided die, apply that mutation operation:

| Die | Mutation |
|-----|----------|
| 1 | Flip one assumption |
| 2 | Invert the constraint |
| 3 | Change the scale (10x bigger or smaller) |
| 4 | Change the time horizon |
| 5 | Merge with a random killed idea's best element |
| 6 | Apply a constraint from a random domain |
| 7 | Remove the most complex component |
| 8 | Add an adversarial requirement |

## External Validation Hooks (TEST extension)

Optional pluggable interface that adds real-world signal to internal scoring:

```typescript
interface ValidationHook {
  name: string;
  validate(idea: Idea, problem: Problem): Promise<{ modifier: number; evidence: string }>;
}
```

Built-in hooks: MarketSearch (existing implementations), FeasibilityCheck (technical blockers), ExpertPanel (async human review), PrototypeSimulation (generate + test prototype).

## Time-Scale Configuration

| Time scale | Budget | Est. cycles | Agents/phase |
|------------|--------|-------------|--------------|
| hours | 5 min | 1-2 | 2-3 |
| days | 12 min | 2-4 | 3-4 |
| weeks | 25 min | 3-8 | 4-5 |
| months | 45 min | 5-15 | 5-6 |
| years | 90 min | 8-30 | 6-8 |
| decades | 180 min | 15-50+ | 8-10 |

## State Persistence

Each run persists to a local working directory:

```
ideate/
  config.json           # Problem, time_scale, domains, hooks
  loop-state.json       # Loop Controller (fitness_history, strategy, decisions)
  domain-pool.json      # Weighted domain pool (expanded across cycles)
  cycle-NNN/            # Per-cycle artifacts: input-pool, dreams, daydreams,
                        # analyses, checkpoint-a, stolen, offspring, scores,
                        # checkpoint-b, survivors, meta-learning, summary
  insights.md           # Insight Extractor output (post-loop)
  final-output.md       # Ranked candidate list with full provenance
```

## Idea Data Structure

```json
{
  "id": "idea-042",
  "text": "...",
  "provenance": {
    "parents": ["idea-017", "idea-023"],
    "operation": "crossover",
    "mutation_type": "scale_change",
    "cycle": 3, "phase": "MATE",
    "source_domains": ["mycology", "distributed-systems"]
  },
  "scores": {
    "feasibility": 72, "novelty": 88, "impact": 65, "elegance": 81,
    "composite": 76.5, "confidence": 0.82, "judge_variance": 8.3
  },
  "arguments": {"supporting": "...", "counter": "..."}
}
```

## Final Output Format

```markdown
# Ideate Results: [Problem]

**Time scale:** [scale] | **Budget used:** X of Y min | **Cycles:** N (adaptive)
**Strategy pivots:** M | **Total ideas:** X | **Survived:** Y | **Kill rate:** Z%

## Top Candidates (ranked by adjusted composite score)

### 1. [Title] — Score: 85.2/100 (confidence: 0.91)
**The idea:** [2-3 sentences]
**Scores:** Feasibility: 78 | Novelty: 92 | Impact: 84 | Elegance: 87
**Provenance:** Born in cycle N from [operation] of [parents]. Mutation: [type].
**For it:** [supporting argument]
**Against it:** [counterargument]

## Evolution Summary
| Cycle | Ideas In | Survived | Top Score | Diversity | Strategy | Decision |

## Meta-Learning Trajectory
- [How strategy evolved across cycles]

## Evolutionary Insights (from The Historian)
- [Dominant lineages, fertile combinations, fitness landscape, problem revelations]
```

## Integration with Other Skills

| Skill | Phase | How |
|-------|-------|-----|
| Research | CONSUME, STEAL | Multi-agent parallel research, cross-domain patterns |
| be-creative | DREAM, DAYDREAM | StandardCreativity workflow for high-noise recombination |
| iterative-depth | CONTEMPLATE | 4-lens analysis (Literal, Failure, Analogical, Constraint Inversion) |
| first-principles | CONTEMPLATE | Decompose to axioms, challenge assumptions |
| red-team | TEST | Adversarial attack on candidates to find fatal flaws |
| Agents | ALL | ComposeAgent for unique cognitive personalities per phase |
| council | MATE (optional) | Debate between ideas before breeding |

## Gotchas

- **Ideate is for multi-cycle evolutionary ideation — not quick brainstorming.** For fast divergent ideas, use be-creative.
- **The Loop Controller manages cycle count — don't override it manually.** Trust the budget-based cycling.
- **Meta-learner adjustments happen automatically within parameter bounds.** Don't manually tune mid-cycle.
- **CONTEMPLATE is mandatory.** Skipping it degrades MATE quality because STEAL operates on disconnected material.
- **Structural randomness defeats LLM bias.** Don't substitute "interesting pairs picked by the LLM" for Fisher-Yates — the bias is the problem.

## Decision: Ideate vs BeCreative

Ideate and BeCreative are kept as **separate skills**, not merged:

- **BeCreative** = single-pass divergent ideation (one shot, 5 diverse candidates, pick the best). Fast, lightweight, output-focused.
- **Ideate** = multi-cycle evolutionary system (9 phases, Loop Controller, fitness scoring, Lamarckian meta-learning). Deep, systematic, process-focused.

This mirrors PAI's own framing: "This is NOT BeCreative." The overlap with `superpowers:brainstorming` is acknowledged — Ideate is for evolutionary ideation with provenance tracking; brainstorming is for collaborative interactive design refinement. Use the right tool for the job.

---

**Attribution:** Adapted from PAI v5.0.0 Ideate skill (Daniel Miessler, MIT-licensed). De-PAI'd for Jack's multi-agent fleet — no Pulse daemon, no bun runtime, no voice notification hooks, no execution log. Structural randomness uses `crypto.randomBytes` or equivalent instead of `crypto.getRandomValues()`.
