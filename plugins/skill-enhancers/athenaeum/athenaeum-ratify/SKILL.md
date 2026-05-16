---
name: athenaeum-ratify
description: Fleet-wide formal attestation of an immutable artifact with dissent recorded, not overruled. Use when a decision needs N-agent sign-off, when chaining ratification onto a converged grill result, or when an ADR/convention should not ship on one agent's say-so. Triggers — "fleet sign off", "ratify this", "N agents approve", "get the fleet's attestation".
---

# Athenaeum — Ratify

## Decision rule: unanimous-or-decompose

- All `SIGN` → **ratified**.
- Any `DISSENT` or `ABSTAIN_BY_TIMEOUT` → **decomposed**. The merge writer aggregates dissent atom-refs and hands them to the human grain-gate. No auto-recursion. No quorum voting.
- `mode: fast` (low-stakes) → any dissent is a plain rejection.

## 3-step workflow

1. **Init** — `scripts/athenaeum init <topic> --mode ratify --roster a,b,c`
   - Freezes artifact verbatim to `artifact.md`. Computes SHA-256. Never edit after init.
   - Writes `manifest.yaml` with roster and `expires_at` (+72h).
   - See `templates/ratify/manifest.yaml.template`.

2. **Vote** — each rostered agent reads `artifact.md`, verifies SHA-256, writes `<agent>.vote.yaml`:
   - `SIGN` — attests the exact bytes.
   - `DISSENT` — proposes atom-refs for decomposition.
   - Agents do not read peers' votes first.
   - See `templates/ratify/vote.yaml.template`.

3. **Tally** — merge writer (first alphabetically among voters) runs:
   - All sign → write `ratified.md`, log `RATIFIED`.
   - Any dissent/abstain → write `decomposition.md`, set `status: pending-human`, ping the human.
   - Human fills `human-decision.yaml`: `accept-split` · `decompose-further` · `rewrite-with-caveats` · `reject`.
   - Merge writer detects the decision and converges.

## Discovery

- `scripts/athenaeum check` — glob open ratifications where this agent is rostered and has not voted.
- n8n can alert the roster, but `check` is the floor — it works even if notifications fail.

## Sibling skills

- `athenaeum-design` — design the artifact before ratifying it
- `athenaeum-reconcile` — reconcile state before ratifying it

Full protocol (caveat rules, grain-gate semantics, terminal events): see `REFERENCE.md` §7–9.
