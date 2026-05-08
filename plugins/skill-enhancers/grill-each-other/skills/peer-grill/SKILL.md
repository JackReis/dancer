---
name: peer-grill
description: Two (or more) agents — Claude sessions, other LLMs, or mixed — interrogate each other through a structured file-based protocol to converge on shared project state. Each agent independently dumps its model, the disagreements get grilled until convergence or surfaced as unresolved, and both sign off on a merged ground truth. Use when the user says "peer-grill", "have the agents grill each other", "reconcile state across sessions", "settle a dispute between sessions", "force two agents to converge on X", "two agents agree on X", or when parallel sessions have diverged.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
version: 2.0.0
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
| `graded.md` | append-only, by `peer_grill_grade.py` | everyone | optional: PASS/FAIL/UNVERIFIABLE table from running `verifier`/`falsifier` blocks on claims |

## Conventions and what's actually enforced

Most rules below are **honor-system conventions** between cooperating agents. Where a script enforces a rule, this is called out.

| Rule | Enforced by |
|---|---|
| An agent never edits another agent's `claims.yaml` | convention only — filesystem permits it |
| `state.merged.yaml` updated only when both agents wrote `RATIFY:` | partial — `peer_grill_check_convergence.py` verifies, but nothing blocks writing the merged file |
| Append-only files never rewritten | convention only — no immutability flag |
| `only-one-knows` items must be grilled at least once | convention only |
| RATIFY requires both agents | yes — `peer_grill_check_convergence.py` |
| Claims dump conforms to schema | partial — `peer_grill_diff.py` runs stdlib structural checks (required fields, enums, id pattern) and emits warnings; full schema validation requires PyYAML + a json-schema validator (out of scope for v1) |

If a script invocation reveals a hard rule was broken, append a `INTEGRITY-FAIL` line to `grill-log.md` and stop — do not proceed with merge or signoff.

## Setup — ask the user before any writes

1. **Topic** — what state are we reconciling? Get a slug.
2. **Identity** — what name is *this* agent? (e.g., `claude-laptop`, `claude-pr-bot`, `cursor-mac`). Must be unique across peers.
3. **Peer** — what's the peer's identity, and how is it accessed (separate Claude session, another model, user-relayed)? If the peer is non-Claude, the user is responsible for getting that peer to follow the same protocol — offer to share `templates/system-prompt-for-non-claude-peer.md` (relative to this skill dir).
4. **Scope** — what categories of claims belong to this reconciliation? (`infra`, `code`, `decision`, `open-work`.) Anything outside these categories is filtered out before diffing.
5. **Round budget** — max grilling rounds per disputed claim before escalating to unresolved (default: 3).

## Protocol

### 1. Independent dump

Write `<agent>.claims.yaml`. **Do not read the peer's file yet.** Each claim minimum-required shape:

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

The full schema (`schemas/claims.schema.json`) accepts richer fields — see "Optional schema fields" below.

Confidence rules:
- `high` requires a *checkable source* (file path + line, command output, signed-off doc).
- `medium` is "I inferred this from X but X may be stale."
- `low` is "I think this is true but I don't have a source."

Stable slugs matter: `db-version`, not `db-version-as-of-may-1`. Same id from different agents = same subject; a different statement = a disagreement, not a collision.

### 2. Symmetric reveal

When both agents' `claims.yaml` files exist, each agent reads the peer's. Polling: re-check every minute up to a 30-minute default timeout. On timeout, append a `TIMEOUT` line to `grill-log.md` and stop — do not proceed with one-sided merge.

### 3. Diff

Compute three buckets:

- **agreed**: same id, same statement (modulo whitespace), compatible scopes. Merge directly.
- **disagreed**: same id, different statements.
- **only-one-knows**: id present in one agent's file, absent from the other's.

`peer_grill_diff.py` does this and appends to `diff.md`. The script also emits structural-schema warnings (required-field, enum, id-pattern checks) but does NOT block on them — the diff still computes.

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
- On convergence, both agents must independently write a RATIFY line to `grill-log.md`. Two header attribution formats are supported by `peer_grill_check_convergence.py`:
  - **Standalone:** an agent-name header line (`[<ISO>] <agent>`) followed by `RATIFY: <claim-id> | <agreed-statement>` on a subsequent line. The agent named in the header is credited.
  - **Inline:** an arrow-form header line (`[<ISO>] <asker> -> <answerer> | claim:<id> | RATIFY: <claim-id> | <agreed-statement>`). The *asker* (left of `->`) is credited.
  The convergence script matches the substring `RATIFY: <claim-id>` to count attribution. The trailing `| <agreed-statement>` is human-readable but not parsed; copy it both times for the audit log.
  Only when both agents have ratified does the claim move to `state.merged.yaml`.

### 5. Merge

Write `state.merged.yaml` with all ratified claims. This step is manual today — no helper script. Format mirrors the dump format minus per-agent fields:

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

Each agent computes `sha256(state.merged.yaml)` (via `peer_grill_signoff.py`) and the script appends to `signoff.md`:

```
agent: <name>
timestamp: <ISO8601>
merged_state_sha256: <hex>
attestation: "I attest the above merged state as the agreed truth as of this timestamp."
```

The signoff script does NOT compare hashes — that's the agent's job. After both agents have signed off, read both lines; if the two `merged_state_sha256` values **don't match**, the protocol failed: somebody edited the merged file between the two reads. Append `INTEGRITY-FAIL` to `grill-log.md`, do not proceed, surface to the user.

### 7. Report

To the user, summarize: converged claim count, unresolved count (with link to `unresolved.md`), peers, sha256 of final state, total rounds spent. Offer to commit `.peer-grill/<topic>/` to git so the reconciliation is auditable.

## Optional schema fields

The full `schemas/claims.schema.json` accepts three optional per-claim blocks beyond the minimum shape:

- **`fingerprint`** — a 4-letter Greek-alphabet visual handle, deterministically derived from `sha256(NFC(id))`. Display-layer only; tools regenerate it from the id rather than trusting an authored value. Compute via `peer_grill_fingerprint.py <claim-id>` (or `--bracketed` for `⟦…⟧` form, or `--batch <claims.yaml>`).
- **`verifier`** / **`falsifier`** — runnable shell commands with `expect:` comparators (literal, numeric, regex, contains, sha256, lines:N). `peer_grill_grade.py <topic-dir>` reads every `*.claims.yaml`, runs these checks, and appends a PASS/FAIL/UNVERIFIABLE/ERROR/FALSIFIED grading table to `graded.md`. Optional but valuable: a `verifier` that another reader can re-run is the strongest source a `high` confidence claim can carry.
- **`disputation`** — full scholastic *quaestio* form (`obiectiones`, `sed_contra`, `respondeo`, `responsiones`, `aletheia_sha256`) for high-stakes contested claims. See the `dialectic-vocabulary` skill in this plugin for the meaning of the Greek/Latin terms. Use sparingly; the structural overhead earns its keep only on claims where the dispute itself needs to be auditable.

## Multi-peer (3+) extension

Run pairwise reconciliations in a chain (A↔B, then merged↔C). Each pairwise run produces a new `state.merged.yaml` that becomes the next pair's input. Document the chain order in `grill-log.md` so a reader can replay it. Star/coordinator topologies are out of scope for v1.

## Guardrails

- **Never** silently accept a one-sided claim. `only-one-knows` items must be grilled at least once.
- **Never** rewrite append-only files; if a correction is needed, append a new entry that supersedes the old one and reference the old one's timestamp.
- **Don't** trust your own confidence levels uncritically — when a peer challenges a `high` claim, re-verify the source rather than restating the assertion.
- **Don't** invent claims to fill gaps. If a scope has no claims, the merged state has no claims in that scope, and that's correct.
- If running this skill *and* the peer is also Claude, suggest the user run each peer in a separate session/terminal so they don't share context — context-sharing defeats the point of independent dumps.

## Helper scripts

All scripts live in `${SKILL_DIR}/scripts/`. `${SKILL_DIR}` resolves to wherever this skill is installed: `~/.claude/skills/peer-grill/scripts/` for a user install, or `<plugin-root>/skills/peer-grill/scripts/` when bundled in a plugin.

| Script | Purpose | Stdlib? |
|---|---|---|
| `peer_grill_init.sh <topic> <agent-name>` | Create `.peer-grill/<topic>/` and stamp the agent identity in a `<agent>.claims.yaml` skeleton | bash only |
| `peer_grill_diff.py <topic-dir>` | Compute three-bucket diff from both `<agent>.claims.yaml` files; emit schema warnings; append diff to `diff.md` | needs PyYAML |
| `peer_grill_check_convergence.py <topic-dir> <claim-id>` | Returns 0 if both agents have written `RATIFY: <claim-id>` to `grill-log.md`, else 1 | stdlib |
| `peer_grill_signoff.py <topic-dir> <agent-name>` | Compute sha256 of `state.merged.yaml`, append signoff line | stdlib |
| `peer_grill_grade.py <topic-dir>` | Run every claim's `verifier`/`falsifier` block; append PASS/FAIL table to `graded.md` | needs PyYAML |
| `peer_grill_fingerprint.py <id-or-claims-yaml>` | Derive Greek-alphabet fingerprint from a claim id (single or batch) | stdlib (`--batch` needs PyYAML) |

PyYAML is the only third-party dependency. Install with `pip install pyyaml` or run from a Python that has it. Scripts emit a clear error and `sys.exit(2)` when PyYAML is missing — they do not silently fall through.

## Relationship to fleet messaging bridges

This skill is **strict file-only**. It does NOT use any session-to-session messaging transport (`hermes-bridge`, `openclaw-bridge`, Discord/Telegram relays, etc.). If you need to wake the peer to start their side of the protocol, do that as a SEPARATE step before invoking peer-grill — the protocol then proceeds via the shared filesystem only. Mixing transports inside the protocol would defeat the BYOM/heterogeneous-fleet goal and re-introduce synchronization bugs the file convention exists to prevent.

## Templates

- `${SKILL_DIR}/templates/claims.yaml.template` — copy-and-fill for the dump phase.
- `${SKILL_DIR}/templates/system-prompt-for-non-claude-peer.md` — paste into a non-Claude peer to teach it the protocol.

## Tests and reference fixtures

- `${SKILL_DIR}/tests/fixtures/two-claims/` — minimal pair of `agent-{a,b}.claims.yaml` files exercising the agreed/disagreed/only-one-knows code paths. Used by `tests/test_diff.py`.
- `${SKILL_DIR}/tests/test_e2e_simulation.py` — full 7-step protocol simulation: init → dump → diff → grill → ratify → merge → signoff. Pre-stages the peer's files in a tempdir and runs the agent-a side through the actual scripts. Verifies both signoff hashes match.

Run all tests: `cd ${SKILL_DIR}/tests && for f in test_*.py; do python3 "$f"; done; bash test_init.sh`. Tests that need PyYAML auto-detect a Python with it; if none is found they print `SKIP` rather than fail.
