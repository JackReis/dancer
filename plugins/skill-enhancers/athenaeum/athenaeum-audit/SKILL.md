---
name: athenaeum-audit
description: Code-aware agent-stack audit + reconcile in one pass. Use when auditing an existing agent topology, reviewing a fleet setup, or triangulating understanding of a codebase's agent architecture across model families. Triggers — "audit the stack", "agent topology review", "fleet audit", "review agent architecture", "triangulate agent state".
---

# Athenaeum — Audit

## When to use what

| Skill | Use when |
|---|---|
| `athenaeum-design` | Building something new; need to settle branches from scratch |
| `athenaeum-reconcile` | Agents already disagree; need structured convergence |
| `athenaeum-audit` | **Reviewing existing architecture**; code-aware triangulation in one pass |

## Pick a mode

| Mode | When to use | Attestation |
|---|---|---|
| `quick` | Verbal read-out, same machine, low stakes | No SHA-256; verbal confidence |
| `formal` | Cross-model, cross-machine, high stakes | Full sign-off with SHA-256 |

Default: `quick` if unspecified.

## 4-step workflow

1. **Init** — `scripts/athenaeum init <topic> --mode audit`
   - Scaffolds `.athenaeum/<topic>/` with audit templates.
   - Prompts for auditor identities and scope.

2. **Dump** — each auditor scans the repo independently.
   - Write `<agent>.claims.yaml` with 13-branch coverage.
   - Do NOT read peer claims yet. Context leakage defeats triangulation.
   - See `templates/reconcile/claims.yaml.template`.

3. **Triangulate** — compute three buckets (same as reconcile):
   - **agreed** → merge directly
   - **disagreed** → grill loop (asker = lower confidence)
   - **only-one-knows** → grill loop (asker = the one who doesn't know)
   - Round budget: 3. Exhaustion → `ESCALATE` to `unresolved.md`.
   - On convergence, both peers write `RATIFY: <id> | <statement>`.

4. **Report** — merge writer writes `audit-report.md`.
   - Findings per branch, confidence levels, source citations, action items.
   - Formal mode: LF-normalize, SHA-256, append to `signoff.md`.
   - See `templates/audit/audit-report.md.template`.

## Code-anchored confidence rules

- `high` — quoted file path + line range AND a verifying read
- `medium` — read it, but artifact may be stale
- `low` — inferred from adjacent files
- No source found → no claim. Do not invent.

## Sibling skills

- `athenaeum-design` — design something before auditing it
- `athenaeum-reconcile` — reconcile divergent state before ratifying
- `athenaeum-ratify` — fleet-wide attestation after audit

Full 13-branch protocol and confidence rules: see `REFERENCE.md` §1.
