# Test Idea Workflow

## Purpose

Test any input across all 11 world models (6 months to 50 years). Returns probability-weighted scenario matrix.

## Inputs

- The idea, strategy, or investment to test
- Optional: tier specification (fast/standard/deep)

## Execution

### Step 1: Decompose the Idea

Break the idea into its core assumptions and claims:
- What must be true for this to succeed?
- What are the key dependencies?
- What are the risk vectors?

### Step 2: First Principles Analysis

Classify each assumption:
- **HARD** — physics/reality, cannot attack
- **SOFT** — policy/choice, can be challenged
- **ASSUMPTION** — unvalidated, prime attack target

### Step 3: Per-Horizon Stress Test

For each of the 11 time horizons (6-month to 50-year), run:
1. RedTeam adversarial analysis of the idea against this horizon's conditions
2. FirstPrinciples challenge of assumptions under this horizon
3. Council debate if multi-perspective analysis is needed

### Step 4: Synthesize

Produce a probability-weighted matrix:

| Horizon | Risk Level | Key Threat | Probability | Mitigation |
|---------|-----------|------------|-------------|------------|
| 6-month | Medium | [threat] | 40% | [mitigation] |
| 1-year | High | [threat] | 65% | [mitigation] |
| ... | ... | ... | ... | ... |

## Standard Tier (~10 min)

Uses 11 parallel agents + RedTeam + FirstPrinciples. Each horizon analyzed in parallel, then synthesized.
