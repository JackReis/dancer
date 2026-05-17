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

## A2A interop

This skill speaks A2A natively. An A2A Task represents this workflow.

**Task metadata:**
- `athenaeum_mode: audit`
- `status` lifecycle: `submitted` → `working` → `input-required` → `completed`

**Artifacts produced:**
- `audit-report.md` — `text/markdown`
- `<agent>.claims.yaml` — `application/yaml`
- `state.merged.yaml` — `application/yaml`

**Enable A2A for this workflow:**
```bash
athenaeum init my-topic --mode audit --transport a2a
```

**Invoking via A2A:**
```json
{
  "jsonrpc": "2.0",
  "method": "tasks/send",
  "params": {
    "task": {
      "id": "athenaeum-audit-my-topic",
      "sessionId": "<agent-session>",
      "status": "submitted",
      "metadata": {"athenaeum_mode": "audit", "topic": "my-topic"}
    }
  }
}
```

## Sibling skills

- `athenaeum-design` — design something before auditing it
- `athenaeum-reconcile` — reconcile divergent state before ratifying
- `athenaeum-ratify` — fleet-wide attestation after audit

### Cross-pack: athenaeum-audit + permutation

- **permutation** (grill-each-other pack) ratifies the NxN relationship matrix — who provides what to whom. After permutation produces `roster.yaml`, that roster seeds athenaeum-audit's auditor list.
- **athenaeum-audit** triangulates architectural understanding. Its topology findings (branch 3) feed into permutation's `workflow` contracts.
- Together: permutation confirms *who talks to whom about what*, audit confirms *what each agent believes about the codebase* — producing a fully validated fleet topology.

Full 13-branch protocol and confidence rules: see `REFERENCE.md` §1.
