---
name: peer-grill
description: Two (or more) agents — Claude sessions, other LLMs, or mixed — interrogate each other through a structured file-based protocol to converge on shared project state. Each agent independently dumps its model, the disagreements get grilled until convergence or surfaced as unresolved, and both sign off on a merged ground truth. Use when parallel sessions have diverged, when reconciling state across machines, or when the user mentions "have the agents grill each other", "peer-grill", "reconcile state", or "two agents agree on X".
---

**Try `agent-show-and-tell` first.** Most fleet-coordination needs are visibility, not consensus — show-and-tell is fire-and-forget, has no failure modes, and surfaces conflicts without trying to resolve them. Reach for `peer-grill` only when show-and-tell has already shown that two agents *meaningfully disagree* about a fact you actually need to settle.

This is a **symmetric, file-based** reconciliation protocol. There is no master and no relay. Each agent reads and writes only specific files in a shared directory. The protocol works whether the peer is another Claude session, a non-Claude LLM, or a human pretending to be one — as long as everyone follows the file conventions.

This skill is invoked by *one* of the peers. It assumes the other peer is independently running the same protocol (or a manual analog). If the other side never shows up, the protocol fails loud at the timeout step rather than silently merging one-sided state.

## Working directory

All artifacts live in `.peer-grill/<topic>/` relative to repo root, where `<topic>` is a short slug for what's being reconciled (e.g. `pricing-decisions`, `infra-state`, `q2-plan`). Default to `default` if the user doesn't specify.

| File | Writers | Readers | Purpose |
|---|---|---|---|
| `<agent>.claims.yaml` | only that agent | everyone | self-reported model of the state |
| `diff.md` | last writer to compute it (append-only) | everyone | three-bucket diff: agreed / disagreed / only-one |
| `grill-log.md` | append-only, both | everyone | full Q&A transcript with timestamps and agent identity |
| `state.merged.yaml` | the **merge writer** (first alphabetically among peers) — once all claims identified in Phase 3 are ratified or escalated. Others read only. | everyone | the converged ground truth |
| `unresolved.md` | append-only, both | everyone | disputes that didn't converge; both positions recorded |
| `signoff.md` | append-only, both | everyone | identity + timestamp + sha256 of `state.merged.yaml` each agent attests to |

**Hard rules:**
- An agent **never** edits another agent's `claims.yaml`.
- `state.merged.yaml` is written only by the **merge writer** — the peer whose name sorts first alphabetically — once all non-agreed claims are either ratified or escalated. The merge writer **overwrites** the file (it's a single-writer batch artifact; appending would produce malformed YAML).
- Append-only files (`grill-log.md`, `signoff.md`, `unresolved.md`) are append-only — never rewrite history.

## Terminal events

The protocol has five terminal-event types. They share a log-line shape `[<ISO>] <self> | <EVENT>: <detail>` written to `grill-log.md`. Phase bodies below cite events by name; this table is the canonical definition.

| Event | Trigger | Phase | Action |
|---|---|---|---|
| `TIMEOUT: phase=<n>` | Poll/wait exhausts `poll_timeout_minutes` | 2, 5 | append; surface to user; stop |
| `PARSE-FAIL: <peer-file>` | Peer's `claims.yaml` fails to parse as YAML on two reads 5 seconds apart | 2 | append; surface to user; stop |
| `IDENTITY-COLLISION` | Peer's `agent` field equals `<self>` | 2 | append; surface to user; stop |
| `ESCALATE: <claim-id>` | Round budget exhausted on a disputed claim | 4 | append; also write both positions to `unresolved.md`; **continue protocol** (only this event doesn't stop) |
| `INTEGRITY-FAIL: <reason>` | Sign-off cannot converge — `reason=iter-loop` (third sha256 mismatch in a row) or `reason=stalled` (5-minute no-activity stall) | 6 | append; surface to user; stop |

## Setup — ask the user before any writes

1. **Topic** — what state are we reconciling? Get a slug.
2. **Identity** — what name is *this* agent? (e.g., `claude-laptop`, `claude-pr-bot`, `cursor-mac`). Must be unique across peers.
3. **Peer** — what's the peer's identity, and how is it accessed (separate Claude session, another model, user-relayed)? If the peer is non-Claude, the user is responsible for getting that peer to follow the same protocol — offer to write a one-page system-prompt summary the user can paste into the peer.
4. **Scope** — what categories of claims belong to this reconciliation? (`infra`, `code`, `decision`, `open-work`, etc.) Anything outside these categories is filtered out before diffing.
5. **Round budget** — max grilling rounds per disputed claim before `ESCALATE` (default: 3).
6. **`poll_timeout_minutes`** — wall-clock budget for polls in Phase 2 and Phase 5 (default: 30). Single configurable parameter applied uniformly; not two independent budgets.

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

### 2. Read & validate peer's claims

Three sequential checks: poll → parse → identity. Each check has one terminal event.

1. **Poll** for `<peer>.claims.yaml` every 60 seconds, up to `poll_timeout_minutes`. On timeout, emit `TIMEOUT: phase=2`.
2. **Parse** the file as YAML. On failure, wait 5 seconds and retry once (handles transient filesystem races where the peer is mid-write). If the second read also fails, emit `PARSE-FAIL: <peer-file>`.
3. **Identity-check.** If the peer's `agent` field equals `<self>`, emit `IDENTITY-COLLISION`. Catching this here — before grilling or merging — prevents both peers from later self-identifying as the alphabetically-first merge writer.

### 3. Diff

Compute three buckets:

- **agreed**: same id, same statement (modulo whitespace), compatible scopes. Merge directly into `state.merged.yaml` with `sources` = the union of both peers' source values for that id (deduplicate identical strings; preserve both peers' citations side-by-side otherwise). Agreed claims do not enter the grill loop and do not require `RATIFY:` lines.
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
- After the round budget is exhausted without convergence, emit `ESCALATE: <claim-id>` per Terminal events. The rest of the protocol continues; only this claim is finalized as unresolved.
- On convergence, both agents must independently write `RATIFY: <claim-id> | <agreed-statement>` lines to `grill-log.md`. Both `<agreed-statement>` values must match exactly modulo leading/trailing whitespace. If they diverge, the claim is *not* ratified — return to the grill loop for that claim. The ratification attempt itself does *not* count as a round; the counter resumes from where it left off after the last actual Q&A round. If the budget was already exhausted when ratification was attempted, no further Q&A is possible and the claim immediately emits `ESCALATE: <claim-id>` per Terminal events.

### 5. Merge

The merge writer waits, up to `poll_timeout_minutes`, for every claim in the `disagreed` and `only-one-knows` buckets to be either ratified (matching `RATIFY:` lines from both peers) or escalated. Agreed-bucket claims skip the grill loop and don't need either; they're merged directly. On timeout, emit `TIMEOUT: phase=5`.

When all non-agreed claims are processed, the merge writer writes `state.merged.yaml` with all agreed claims plus all ratified claims. (Per Hard rules: only the merge writer writes; the file is overwritten, never appended.)

The non-writer peer polls for the file's appearance with the same `poll_timeout_minutes` and proceeds to Phase 6 once it's present. On timeout, emit `TIMEOUT: phase=5`.

Format mirrors the dump format minus per-agent fields:

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

Compute `sha256` of `state.merged.yaml` after **LF-normalizing** the file content (strip any `\r` — cross-platform line endings are otherwise the most likely cause of stable-but-divergent hashes). Append to `signoff.md`:

```
agent: <name>
timestamp: <ISO8601>
merged_state_sha256: <hex>
attestation: "I attest the above merged state as the agreed truth as of this timestamp."
```

**Mismatch handling.** Iteration is normal — sha256 mismatches do *not* immediately escalate. Any agent that observes a mismatch with the peer's signoff re-reads `state.merged.yaml` (LF-normalized), recomputes their own sha256, and either confirms it still matches their last signoff (no further action) or appends a *superseding* signoff entry referencing their own prior signoff's timestamp:

```
agent: <name>
timestamp: <new ISO8601>
merged_state_sha256: <new hex>
supersedes: <prior timestamp from this agent>
attestation: "I attest the above merged state as the agreed truth as of this timestamp."
```

This is symmetric — the merge writer can have a stale hash too. Don't defer to a "later signer."

Emit `INTEGRITY-FAIL: <reason>` (per Terminal events) in exactly two cases:
- `iter-loop`: third sha256 mismatch in a row, i.e. two of *your own* supersedes without convergence. Indicates the merge writer is editing in a loop the other peer can't keep up with.
- `stalled`: mismatch persists 5 minutes with no new entry in `signoff.md` or `grill-log.md` and your hash is stable.

### 7. Report

To the user, summarize: converged claim count, unresolved count (with link to `unresolved.md`), peers, sha256 of final state, total rounds spent. Offer to commit `.peer-grill/<topic>/` to git so the reconciliation is auditable.

## Use case: teaching the skills framework via reconciliation

Peer-grill doubles as a teaching mechanism when one peer knows something the other doesn't. The asymmetry surfaces during step 3 as `only-one-knows` items, and step 4 forces the less-informed peer to grill the more-informed one until the claim is verified and ratified.

**Concrete recipe — teaching the Claude skills framework to a non-Claude agent:**

1. Set `topic = skills-framework`.
2. The Claude peer's `claims.yaml` enumerates what exists: each skill's id, location, purpose, and the rules of the framework itself (frontmatter format, trigger phrases, working-directory conventions).
3. The non-Claude peer's `claims.yaml` is mostly empty (or contains its current — possibly wrong — model of how skills work).
4. Steps 3–4 run normally. Every skill becomes an `only-one-knows` item; the non-Claude peer grills the Claude peer on each one until the source citations are convincing.
5. The merged `state.merged.yaml` becomes a verified, peer-attested description of the framework that the non-Claude agent now genuinely understands — not just was told.

This works for any framework, doc set, or shared mental model — not just skills. Pick `topic` to match what's being taught.

## Multi-peer (3+) extension

For N-agent consensus or ratification of a single artifact, use the **`fleet-ratify`** skill instead. `peer-grill` is optimized for 1:1 reconciliation of broad state; `fleet-ratify` is the capstone for N agents signing a specific, frozen artifact.

Pairwise reconciliations in a chain (A↔B, then merged↔C) are still supported in `peer-grill` for broad state sync, but for formal decision-making by the whole fleet, `fleet-ratify` is the preferred path. Document the chain order in `grill-log.md` if using the chain method.

## Guardrails

- **Never** silently accept a one-sided claim. `only-one-knows` items must be grilled at least once.
- **Never** rewrite append-only files; if a correction is needed, append a new entry that supersedes the old one and reference the old one's timestamp.
- **Don't** trust your own confidence levels uncritically — when a peer challenges a `high` claim, re-verify the source rather than restating the assertion.
- **Don't** invent claims to fill gaps. If a scope has no claims, the merged state has no claims in that scope, and that's correct.
- If running this skill *and* the peer is also Claude, suggest the user run each peer in a separate session/terminal so they don't share context — context-sharing defeats the point of independent dumps.
