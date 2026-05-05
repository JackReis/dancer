---
name: peer-grill
description: Two (or more) agents — Claude sessions, other LLMs, or mixed — interrogate each other through a structured file-based protocol to converge on shared project state. Each agent independently dumps its model, the disagreements get grilled until convergence or surfaced as unresolved, and both sign off on a merged ground truth. This skill should be used when the user asks to "peer-grill", "have the agents grill each other", "reconcile state across sessions", "two agents agree on X", or when parallel sessions have diverged.
---

This is a **symmetric, file-based** reconciliation protocol. There is no master and no relay. Each agent reads and writes only specific files in a shared directory. The protocol works whether the peer is another Claude session, a non-Claude LLM, or a human pretending to be one — as long as everyone follows the file conventions.

This skill is invoked by *one* of the peers. It assumes the other peer is independently running the same protocol (or a manual analog). If the other side never shows up, the protocol fails loud at the timeout step rather than silently merging one-sided state.

## Working directory

All artifacts live in `.peer-grill/<topic>/` relative to repo root, where `<topic>` is a short slug for what's being reconciled (e.g. `pricing-decisions`, `infra-state`, `q2-plan`). Default to `default` if the user doesn't specify.

| File | Writers | Readers | Purpose |
|---|---|---|---|
| `<agent>.claims.yaml` | only that agent | everyone | self-reported model of the state |
| `diff.md` | last writer to compute it (append-only) | everyone | three-bucket diff: agreed / disagreed / only-one |
| `grill-log.md` | append-only, both | everyone | full Q&A transcript with timestamps and agent identity |
| `state.merged.yaml` | only after both agents append a consensus marker to `grill-log.md` | everyone | the converged ground truth |
| `unresolved.md` | append-only, both | everyone | disputes that didn't converge; both positions recorded |
| `signoff.md` | append-only, both | everyone | identity + timestamp + sha256 of `state.merged.yaml` each agent attests to |

**Hard rules:**
- An agent **never** edits another agent's `claims.yaml`.
- `state.merged.yaml` is updated only when `grill-log.md` shows both agents wrote `RATIFY: <claim-id>` for that claim.
- Append-only files are append-only — never rewrite history.

## Setup — ask the user before any writes

1. **Topic** — what state are we reconciling? Get a slug.
2. **Identity** — what name is *this* agent? (e.g., `claude-laptop`, `claude-pr-bot`, `cursor-mac`). Must be unique across peers.
3. **Peer** — what's the peer's identity, and how is it accessed (separate Claude session, another model, user-relayed)? If the peer is non-Claude, the user is responsible for getting that peer to follow the same protocol — offer to write a one-page system-prompt summary the user can paste into the peer.
4. **Scope** — what categories of claims belong to this reconciliation? (`infra`, `code`, `decision`, `open-work`, etc.) Anything outside these categories is filtered out before diffing.
5. **Round budget** — max grilling rounds per disputed claim before escalating to unresolved (default: 3).

## Protocol

### 1. Independent dump

Write `<agent>.claims.yaml`. **Do not read the peer's file yet.** Each claim is:

```yaml
agent: <agent-name>
session_started: <ISO8601>
scope: [infra, code, decision, open-work]
claims:
  - id: <stable-slug>            # same id across agents = same subject
    statement: <one sentence>
    confidence: high | medium | low
    source: <how you know — file path, command, observation, prior decision>
    scope: <one of the declared scopes>
    last_verified: <ISO8601 or "unknown">
```

Confidence rules:
- `high` requires a *checkable source* (file path + line, command output, signed-off doc).
- `medium` is "I inferred this from X but X may be stale."
- `low` is "I think this is true but I don't have a source."

Stable slugs matter: `db-version`, not `db-version-as-of-may-1`. Same id from different agents = same subject; a different statement = a disagreement, not a collision.

### 2. Symmetric reveal

When both agents' `claims.yaml` files exist, each agent reads the peer's. (Polling: re-check every minute up to a 30-minute default timeout. On timeout, append a `TIMEOUT` line to `grill-log.md` and stop — do not proceed with one-sided merge.)

### 3. Diff

Compute three buckets:

- **agreed**: same id, same statement (modulo whitespace), compatible scopes. Merge directly.
- **disagreed**: same id, different statements.
- **only-one-knows**: id present in one agent's file, absent from the other's.

Append the diff to `diff.md` as a single block, prefixed with timestamp and which agent wrote it. If the peer also wrote a diff, compare them — *diffs-of-diffs catch silent-drop bugs*. Any divergence between the two computed diffs is itself a disagreement to resolve before grilling claims.

### 4. Grill loop

For each item in `disagreed` and `only-one-knows`, in `grill-log.md`:

```
[<ISO>] <asker> -> <answerer> | claim:<id> | round:1
Q: <question — must include the specific phrasing or source you doubt>
[<ISO>] <answerer> -> <asker> | claim:<id> | round:1
A: <answer — must cite a source the asker can in principle verify>
```

Rules:
- For `disagreed` claims, the agent with the *lower* confidence asks first. Ties broken alphabetically by agent name.
- For `only-one-knows`, the agent who *doesn't* know asks.
- An answer that doesn't cite a verifiable source is grounds for another round.
- After the round budget is exhausted without convergence, write `ESCALATE: <claim-id>` and append both positions to `unresolved.md`.
- On convergence, both agents must independently write `RATIFY: <claim-id> | <agreed-statement>` lines to `grill-log.md`. RATIFY lines may be inline with an asker→answerer header line OR grouped under a standalone agent-identifier line `[<ISO>] <agent-name>` followed by one or more RATIFY lines (the convergence checker accepts either form). Only when both agents have ratified does the claim move to `state.merged.yaml`.

### 5. Merge

Write `state.merged.yaml` with all ratified claims. Format mirrors the dump format minus per-agent fields:

```yaml
topic: <topic>
ratified_at: <ISO8601>
peers: [<agent-a>, <agent-b>]
claims:
  - id: <id>
    statement: <agreed statement>
    sources: [<from agent-a>, <from agent-b>]   # both sources preserved
    scope: <scope>
```

### 6. Sign-off

Each agent computes `sha256(state.merged.yaml)` and appends to `signoff.md`:

```
agent: <name>
timestamp: <ISO8601>
merged_state_sha256: <hex>
attestation: "I attest the above merged state as the agreed truth as of this timestamp."
```

If the two sha256 values **don't match**, the protocol failed — somebody edited the merged file between the two reads. Append `INTEGRITY-FAIL` to `grill-log.md`, do not proceed, surface to the user.

### 7. Report

To the user, summarize: converged claim count, unresolved count (with link to `unresolved.md`), peers, sha256 of final state, total rounds spent. Offer to commit `.peer-grill/<topic>/` to git so the reconciliation is auditable.

## Multi-peer (3+) extension

Run pairwise reconciliations in a chain (A↔B, then merged↔C). Each pairwise run produces a new `state.merged.yaml` that becomes the next pair's input. Document the chain order in `grill-log.md` so a reader can replay it. Star/coordinator topologies are out of scope for v1.

## Guardrails

- **Never** silently accept a one-sided claim. `only-one-knows` items must be grilled at least once.
- **Never** rewrite append-only files; if a correction is needed, append a new entry that supersedes the old one and reference the old one's timestamp.
- **Don't** trust your own confidence levels uncritically — when a peer challenges a `high` claim, re-verify the source rather than restating the assertion.
- **Don't** invent claims to fill gaps. If a scope has no claims, the merged state has no claims in that scope, and that's correct.
- If running this skill *and* the peer is also Claude, suggest the user run each peer in a separate session/terminal so they don't share context — context-sharing defeats the point of independent dumps.

## Helper scripts

All scripts live in `${SKILL_DIR}/scripts/` (i.e. `~/.claude/skills/peer-grill/scripts/`). Invoke with absolute paths.

| Script | Purpose | Args |
|---|---|---|
| `peer_grill_init.sh <topic> <agent-name>` | Create `.peer-grill/<topic>/` and stamp the agent identity in `<agent>.claims.yaml` skeleton | topic slug, agent name |
| `peer_grill_diff.py <topic-dir>` | Compute three-bucket diff from both `<agent>.claims.yaml` files; appends to `diff.md` | absolute path to topic dir |
| `peer_grill_check_convergence.py <topic-dir> <claim-id>` | Returns 0 if both agents have written `RATIFY: <claim-id>` to `grill-log.md`, else 1 | topic dir, claim id |
| `peer_grill_signoff.py <topic-dir> <agent-name>` | Compute sha256 of `state.merged.yaml`, append signoff line | topic dir, agent name |

Scripts are pure stdlib (Python 3.11 + bash). No MCP dependencies — they work whether the peer is a Claude session, Hermes, Zoe, KimiClaw, PT/Gemini CLI, or a human.

## Relationship to fleet messaging bridges

This skill is **strict file-only**. It does NOT call `autonomous-ai-agents:hermes-bridge`, `autonomous-ai-agents:openclaw-bridge`, or `dizzy.py`. If you need to wake the peer to start their side of the protocol, do that as a SEPARATE step before invoking peer-grill — the protocol then proceeds via the shared filesystem only. Mixing transports inside the protocol would defeat the BYOM/heterogeneous-fleet goal and re-introduce the synchronization bugs the file convention exists to prevent.

## Templates

`${SKILL_DIR}/templates/claims.yaml.template` — copy-and-fill for the dump phase.
`${SKILL_DIR}/templates/system-prompt-for-non-claude-peer.md` — paste into a non-Claude peer to teach it the protocol.

## Reference fixture

A working real-world example lives at `/Users/jack.reis/Documents/=notes/.peer-grill/matrix-mcp-shim-path/` (matrix MCP shim path reconciliation between two Claude sessions, 2026-05-03). Use it as a worked example of all 7 artifact types.
