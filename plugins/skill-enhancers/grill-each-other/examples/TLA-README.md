# Formalization — load-bearing claims as TLA+

This directory holds formal specs for high-stakes claims in the session-equipment grill. Each spec lives at the rung of the load-bearing ladder where the cost-of-getting-it-wrong justifies the cost-of-formalizing.

## What's here

| File | Claim | Why formalize |
|---|---|---|
| `CompactHandoffPrivacy.tla` | `suggestion-G` (`/compact` handoff cross-agent visibility) | The prose hand-waves "needs a privacy gate." TLA+ forces us to say WHICH gate (Sanitize), on WHICH state (UserOrigin ∩ ¬Vault), with WHICH guarantee ([]PrivacySafe). The four LIMITS at the bottom of the spec become four follow-up grill branches a reviewer can target. |

## Reading these as documentation (no TLC required)

You don't need to run TLC to get value from these. The spec format is:

1. **CONSTANTS** — what abstract entities exist (Tokens, UserOrigin, …)
2. **VARIABLES** — what state evolves (summary, vault, handoff)
3. **Init / Next** — initial state + valid transitions
4. **Invariants** — what must hold in every reachable state
5. **Theorems** — claims about the spec itself
6. **Notes-on-what-this-doesn't-model** — explicit transparency about the spec's limits

The "doesn't-model" section is intentionally load-bearing. Every limit named there is a place the prose was vague and the formalization made the vagueness visible. **A reviewer who finds a NEW limit that isn't in the list has produced a falsification.**

## Running TLC (optional)

```bash
# Install TLA+ tools (one-time)
brew install --cask tla-plus-toolbox          # GUI
# or grab tla2tools.jar from github.com/tlaplus/tlaplus

# Model-check the safe spec — should report "0 errors found"
java -jar tla2tools.jar -workers auto -config CompactHandoffPrivacy.cfg CompactHandoffPrivacy.tla
```

A `.cfg` file isn't checked in yet — generating one is part of the next-rung formalization. For now the spec serves as **rigorous documentation that survives prose drift**, even without a model checker.

## When to climb to this rung

Per `feedback_load_bearing_via_verifiers`:

| Rung | When to use |
|---|---|
| Prose | Brainstorm, low-stakes opinions |
| Structured prose (YAML claims) | Default for grills |
| Schema-validated YAML | When dumps need cross-agent compat |
| Executable verifiers | Empirical claims with checkable state |
| **Formal spec (TLA+ / Alloy)** | **High-stakes invariants where being wrong has compounding cost (privacy, safety, correctness)** |
| Mechanized proof (Lean / Coq) | Foundational properties, security kernels |

Suggestion-G earns its way to this rung because the failure mode (leaking unredacted user tokens cross-agent) is silent and reversible-only-via-detection. Worth the spec.
