---
name: athenaeum-reconcile
description: Two or more agents reconcile divergent understanding through a structured file-based protocol. Use when parallel sessions disagree, when a non-Claude peer needs to converge with a Claude session, or when triangulating a design across model families. Triggers — "agents disagree", "reconcile state", "peer grill", "triangulate", "two agents audit this".
---

# Athenaeum — Reconcile

## Pick a mode

| Mode | When to use | Attestation |
|---|---|---|
| `quick` | Low-stakes, trust-high, same machine | Verbal agreement; no SHA-256 |
| `formal` | High-stakes, cross-machine, cross-model | Full protocol with sign-offs |

Default: `quick` if unspecified.

## 4-step workflow

1. **Init** — `scripts/athenaeum init <topic> --mode quick|formal`
   - Scaffolds `.athenaeum/<topic>/` with templates.
   - Prompts for identities and scope.

2. **Dump** — each peer writes `<agent>.claims.yaml` independently.
   - Do NOT read peer files yet. Context leakage defeats triangulation.
   - See `templates/reconcile/claims.yaml.template`.

3. **Diff & grill** — compute three buckets:
   - **agreed** → merge directly
   - **disagreed** → grill loop (asker = lower confidence)
   - **only-one-knows** → grill loop (asker = the one who doesn't know)
   - Round budget: 3. Exhaustion → `ESCALATE` to `unresolved.md`.
   - On convergence, both peers write `RATIFY: <id> | <statement>`.

4. **Merge & sign** — merge writer writes `state.merged.yaml`.
   - Formal mode: LF-normalize, SHA-256, append to `signoff.md`.
   - Quick mode: verbal sign-off; write `state.merged.yaml` without crypto.

## Non-Claude peers

Paste the one-page prompt from `templates/reconcile/peer-prompt.md` into the peer session. The protocol is symmetric — no Claude-specific assumptions.

## Sibling skills

- `athenaeum-design` — design something before reconciling it
- `athenaeum-ratify` — formal fleet attestation after reconciliation

Full protocol (formal mode terminal events, integrity failures, multi-peer chains): see `REFERENCE.md` §3–6.
