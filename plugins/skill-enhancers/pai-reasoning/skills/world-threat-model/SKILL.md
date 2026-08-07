---
name: world-threat-model
description: Persistent world-model harness that stress-tests ideas, strategies, and investments against 11 time horizons from 6 months to 50 years. Each horizon model is a deep (~10 page) analysis of geopolitics, technology, economics, society, environment, security, and wildcards. Four workflows: TestIdea (test any input across all 11 horizons, returns probability-weighted scenario matrix), UpdateModels (refresh model content with new research), ViewModels (read and summarize current state), TestScenario (test against alternative future models). Orchestrates red-team, first-principles, and council internally. USE WHEN threat model, world model, test idea, test strategy, test investment, how will this hold up, long-term risk, what could go wrong over time, horizon analysis, crash scenario.
---

# World Threat Model Harness

A system of 11 persistent world models spanning 6 months to 50 years. Each model is a deep (~10 page) analysis of geopolitics, technology, economics, society, environment, security, and wildcards for that time horizon. Ideas, strategies, and investments are tested against ALL horizons simultaneously using adversarial analysis.

## Workflow Routing

| Trigger | Workflow | Description |
|---------|----------|-------------|
| "test idea", "test strategy", "test investment", "how will this hold up", "stress test", "test against future" | `Workflows/TestIdea.md` | Test any input across all 11 world models |
| "update world model", "update models", "refresh models", "new analysis" | `Workflows/UpdateModels.md` | Refresh world model content with new research/analysis |
| "view world model", "show models", "current models", "model status" | `Workflows/ViewModels.md` | Read and summarize current world model state |

## Tier System

All workflows support three execution tiers:

| Tier | Target Time | Strategy | When to Use |
|------|-------------|----------|-------------|
| **Fast** | ~2 min | Single agent synthesizes across all models | Quick gut-check, casual exploration |
| **Standard** | ~10 min | 11 parallel agents + red-team + first-principles | Most use cases, good depth/speed balance |
| **Deep** | Up to 1 hr | 11 parallel agents + per-horizon Research + red-team + first-principles | High-stakes decisions, major investments |

**Default tier:** Standard. User specifies with "fast" or "deep".

## World Model Storage

Models are stored at: `resources/world-models/`

### Horizon Models (base views)

| File | Horizon |
|------|---------|
| `INDEX.md` | Summary of all models with last-updated dates |
| `6-month.md` | 6-month outlook |
| `1-year.md` | 1-year outlook |
| `2-year.md` | 2-year outlook |
| `3-year.md` | 3-year outlook |
| `5-year.md` | 5-year outlook |
| `7-year.md` | 7-year outlook |
| `10-year.md` | 10-year outlook |
| `15-year.md` | 15-year outlook |
| `20-year.md` | 20-year outlook |
| `30-year.md` | 30-year outlook |
| `50-year.md` | 50-year outlook |

### Scenario Models (alternative futures)

Stored at: `resources/world-models/Scenarios/`

| File | Scenario |
|------|----------|
| `great-correction-2027.md` | Severe US crash (2027 ± 12mo) — AI capex burst + housing + credit cascade |

## Context Files

| File | Purpose |
|------|---------|
| `ModelTemplate.md` | Template structure for world model documents |
| `OutputFormat.md` | Template for TestIdea results output |

## Skill Integrations

This skill orchestrates multiple capabilities:

- **red-team** — Adversarial stress testing of ideas against each horizon
- **first-principles** — Decompose idea assumptions into hard/soft/assumption constraints
- **council** — Multi-perspective debate on idea viability across horizons
- **research** — Deep research for model creation and updates

## Gotchas

- **11 time horizons (6mo-50yr).** Don't over-index on short-term predictions — the value is in long-term structural analysis.
- **Threat models are hypothetical.** Present as scenarios with probability ranges, not predictions.
- **Update models when major world events occur.** Static threat models decay in accuracy.

## Examples

**Example 1: Test an investment thesis**
```
User: "threat model my bet on AI-first content creation"
→ Analyzes across 11 time horizons (6mo to 50yr)
→ Identifies structural risks at each horizon
→ Returns probability-weighted scenario matrix
```

**Example 2: Stress test a strategy**
```
User: "what could go wrong with our newsletter business model?"
→ Maps threat vectors: market, technology, regulatory, competitive
→ Returns prioritized risk register with mitigations
```

---

**Attribution:** Adapted from PAI v5.0.0 WorldThreatModel skill (Daniel Miessler, MIT-licensed). De-PAI'd for Jack's multi-agent fleet — no Pulse daemon, no bun runtime, no voice notification hooks, no execution log. Model storage path adjusted to pack-relative `resources/world-models/`.
