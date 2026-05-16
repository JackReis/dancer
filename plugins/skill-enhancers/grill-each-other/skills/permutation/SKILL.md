---
name: permutation
description: |
  Ratify the NxN relationship matrix of a fleet — for every ordered pair of agents,
  confirm what each expects from and provides to the other, and write the result
  to structured JSON + markdown with an n8n webhook payload for immutable custody.
  Use when onboarding a new agent into a fleet, when agent roles change, when
  handoff protocols need explicit confirmation, or when the user says
  "permutation", "fleet topology", "relationship matrix", "who does what for whom",
  "ratify fleet relationships", or "NxN agent mapping".
allowed-tools: Read, Write, Bash, Edit
version: 1.0.0
---

# Permutation

## What it does

For every ordered pair (A → B) in a fleet, `permutation` produces a confirmed
relationship entry describing what A expects from B, what B expects from A, and
the workflow contract between them. The result is a complete NxN matrix — the
**fleet topology map** — ratified by each agent for its own row and written to
JSON, markdown, and an n8n webhook payload for immutable custody.

This is not `fleet-ratify` (which ratifies an *artifact*). Permutation ratifies
**inter-agent relationships** — the edges, not the nodes.

## When to use

- A new agent joins the fleet (onboarding)
- An existing agent's role, capabilities, or responsibilities change
- A handoff protocol needs explicit confirmation from both sides
- The fleet topology needs to be documented and version-controlled
- Before or after a `fleet-ratify` round, to confirm the *who-talks-to-whom*
  is correct
- After `agent-show-and-tell`, when you need to crystallize discovered
  relationships into a confirmed contract

## When not to use

- Two agents reconciling specific state (use `peer-grill`)
- Ratifying a decision or document (use `fleet-ratify`)
- Visibility without commitment (use `agent-show-and-tell`)
- A single agent self-describing (use `agent-show-and-tell`)

## Protocol

### 1. Initiate

The initiator (any agent) creates the permutation state directory and manifest.

```bash
permutation init --roster agent-a,agent-b,agent-c [--topic <slug>]
```

Working directory: `.permutation/<topic>/` (default topic: `fleet-topology-YYYY-MM-DD`).

The initiator writes:

- `manifest.yaml` — roster, topic, initiator, `expires_at`, status
- `roster.yaml` — identity cards for each agent (facets from `agent-show-and-tell`)
- `matrix.json` — empty NxN structure, ready for each agent's row
- `matrix.md` — empty human-readable table

If n8n is configured, the initiator sends an `init` payload to the n8n webhook:

```json
{
  "event": "permutation.init",
  "topic": "<topic>",
  "roster": ["agent-a", "agent-b", "agent-c"],
  "initiated_at": "<ISO8601>",
  "initiated_by": "<agent>"
}
```

### 2. Discover

Each agent fills its own **row** of the matrix — the A→B entries for every other
agent B. For each pair, the agent writes:

```yaml
# <agent-a>.row.yaml
from: agent-a
entries:
  - to: agent-b
    provides:                    # what A provides TO B
      - "CI/CD pipeline status updates"
      - "PR review notifications"
    expects:                    # what A expects FROM B
      - "Deployment approvals within 2h"
      - "Incident escalation handoff"
    workflow:                   # the contract between A and B
      trigger: "PR merged to main"
      channel: "slack:#deployments"
      format: "structured notification"
      sla: "2h response for approvals"
    confidence: high | medium | low
    notes: optional free-text
  - to: agent-c
    provides: [...]
    expects: [...]
    workflow: {...}
    confidence: ...
```

Rules:
- Each agent fills **only its own row**. Never edit another agent's row.
- An agent may discover it doesn't know enough about another agent to fill
  details. Write what you know, set `confidence: low`, and add to `notes:`.
- `provides` and `expects` are promises — they represent what this agent
  *commits to* providing or *genuinely needs*, not wishful thinking.
- The `workflow` block is the **contract** between A and B. It's the
  handoff protocol — trigger, channel, format, and SLA.

### 3. Cross-check

When all agents have written their rows, the merge writer (first alphabetically
among agents who submitted rows) cross-checks the matrix:

For each unordered pair {A, B}:
- Read `A.row → to: B` and `B.row → to: A`
- Check that A's `expects from B` aligns with B's `provides to A` (and vice versa)
- Flag mismatches, asymmetries, and gaps

The merge writer produces:
- `cross-check.md` — human-readable cross-check results with alignment scores
- `cross-check.json` — machine-readable results

And sends a `cross-check` payload to n8n:

```json
{
  "event": "permutation.cross-check",
  "topic": "<topic>",
  "aligned": 5,
  "misaligned": 2,
  "gaps": 1,
  "pairs": [
    {"from": "agent-a", "to": "agent-b", "status": "aligned"},
    {"from": "agent-a", "to": "agent-c", "status": "misaligned", "detail": "A expects Slack notifications from C, but C provides email only"}
  ]
}
```

### 4. Ratify

Each agent reviews the cross-check for its row. For each pair:

- **aligned** → `SIGN` (the relationship as described matches reality)
- **misaligned** → `DISSENT` with specifics about what's wrong
- **gap** → `NOTE` with what's missing (e.g., "I didn't know C provides
  deployment rollbacks — that's useful, I'll add expecting that")

Each agent writes `<agent>.ratify.yaml`:

```yaml
agent: agent-a
topic: fleet-topology
timestamp: 2026-05-16T18:00:00Z
decisions:
  - pair: [agent-a, agent-b]
    verdict: SIGN
  - pair: [agent-a, agent-c]
    verdict: DISSENT
    reason: "C provides email notifications but my workflow expects Slack"
notes: "Need to add rollback expectation from C"
```

### 5. Converge

The merge writer tallies ratifications:

- All pairs `SIGN` → write `ratified-matrix.json` and `ratified-matrix.md`
  with the confirmed fleet topology
- Any `DISSENT` or `NOTE` → write `convergence-gaps.md` with the issues,
  set `status: pending-convergence`, ping the human

The human reviews gaps, decides how to resolve them, and the cycle re-opens
for affected pairs only.

### 6. Finalize

On full ratification, the merge writer:

1. Writes `ratified-matrix.json` — the canonical NxN matrix
2. Writes `ratified-matrix.md` — human-readable topology map
3. Computes `SHA-256` of `ratified-matrix.json`
4. Sends `permutation.finalize` payload to n8n for immutable custody

```json
{
  "event": "permutation.finalize",
  "topic": "<topic>",
  "roster": ["agent-a", "agent-b", "agent-c"],
  "sha256": "<hash>",
  "ratified_at": "<ISO8601>",
  "pairs_confirmed": 6,
  "artifacts": [
    "ratified-matrix.json",
    "ratified-matrix.md"
  ]
}
```

The n8n payload is **immutable custody** — it proves the topology was ratified
at a specific point in time, with specific content, by specific agents. This
is the same principle as `fleet-ratify`'s SHA-256 attestation, but for
*relationships* rather than *decisions*.

## Working directory

All state lives in `.permutation/<topic>/` under the repo root.

| File | Writers | Purpose |
|---|---|---|
| `manifest.yaml` | initiator | roster, topic, expires_at, status |
| `roster.yaml` | initiator (from show-and-tell facets or manual) | identity cards for each agent |
| `matrix.json` | merge writer (assembled from rows) | the NxN matrix being built |
| `matrix.md` | merge writer | human-readable matrix table |
| `<agent>.row.yaml` | only that agent | A's expectations of and provisions to all other agents |
| `cross-check.md` | merge writer | alignment analysis |
| `cross-check.json` | merge writer | machine-readable alignment results |
| `<agent>.ratify.yaml` | only that agent | ratification decisions per pair |
| `convergence-gaps.md` | merge writer | unresolved misalignments for human review |
| `ratified-matrix.json` | merge writer (terminal) | confirmed NxN topology with SHA-256 |
| `ratified-matrix.md` | merge writer (terminal) | human-readable confirmed topology map |
| `log.md` | append-only, all | timestamped event log |

## n8n webhook payload format

All payloads share a common envelope:

```json
{
  "schema": "permutation-v1",
  "topic": "<topic>",
  "event": "init | discover | cross-check | ratify | converge | finalize | gap | fail",
  "timestamp": "<ISO8601 UTC>",
  "agent": "<agent-slug>",
  "payload": { ... }
}
```

The webhook URL is read from `PERMUTATION_N8N_WEBHOOK` env var or
`.permutation/<topic>/manifest.yaml` `n8n_webhook_url` field. If neither is set,
n8n payloads are skipped — the protocol still works via filesystem alone.

## Relationship to other skills

| Skill | Ratifies | Scope |
|---|---|---|
| `fleet-ratify` | An artifact (document, decision, ADR) | 1 artifact, N agents |
| `permutation` | Inter-agent relationships | NxN pairs, fleet topology |
| `agent-show-and-tell` | Nothing (visibility only) | 1 report per agent, no commitment |
| `peer-grill` | Nothing (reconciliation) | 2 agents, specific state |

A typical fleet coordination flow:

1. `agent-show-and-tell` — discover what each agent knows and does
2. **`permutation`** — ratify the relationships discovered in step 1
3. `fleet-ratify` — ratify any decisions that emerge from the confirmed topology

## Common mistakes

| Mistake | Fix |
|---|---|
| Filling another agent's row | Only write `<your-agent>.row.yaml`. Other agents fill their own. |
| Writing what you *wish* B provided instead of what B *actually* provides | Be honest. Gaps go in `notes:` with `confidence: low`. The cross-check catches dishonesty. |
| Skipping the cross-check | The cross-check is how A's "expects" aligns with B's "provides". Without it the matrix is just two unverified wish lists. |
| Ratifying a pair you didn't actually check | Read the other agent's row for that pair before ratifying. |
| Treating ratified-matrix as static forever | Topology changes. Re-run permutation when agents are added, removed, or roles change. |

## Quick reference

| Command | Does |
|---|---|
| `permutation init --roster a,b,c` | Create manifest, empty matrix, roster |
| `permutation discover` | Find permutations awaiting your row |
| `permutation check` | Find permutations awaiting your ratification |
| `permutation cross-check <topic>` | Merge writer: run alignment analysis |
| `permutation tally <topic>` | Merge writer: tally ratifications |

The CLI is a convenience wrapper. The protocol — not the CLI — is the contract.
If the commands aren't installed, perform each step by hand, writing files
directly per the templates.

## Reference

Templates: `templates/`. Full fleet-ratification design:
`=notes/docs/plans/2026-05-16-fleet-ratification-design.md`.