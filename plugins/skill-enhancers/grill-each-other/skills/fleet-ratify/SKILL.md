---
name: fleet-ratify
description: Use when the fleet must formally sign off on an artifact — a converged grill result, a vault doc, an ADR, a convention, or a proposition — and one agent's or a pair's approval is not enough. Use when chaining ratification onto a finished grill, or when a decision needs N-agent attestation with dissent recorded rather than overruled.
---

# Fleet Ratify

## Overview

`fleet-ratify` gets N fleet agents to formally attest to an artifact. The
rule: **nothing is ratified while a substantive objection stands** — but
dissent does not kill the artifact, it triggers decomposition. The artifact is
**immutable**; ratification is an **attestation layer** over it, never a
re-sliced document.

It is the capstone of the `grill-each-other` pack. For two agents reconciling
state, use `peer-grill`. For fleet visibility without consensus, use
`agent-show-and-tell`. Reach for `fleet-ratify` only when a decision genuinely
needs the whole roster's signature.

## When to Use

- A converged grill result (`grill-me`, `peer-grill`, `grill-with-docs`) needs
  fleet sign-off before it binds.
- An ADR, convention, or plan should not ship on one agent's say-so.
- A proposition needs N-agent attestation with dissent **recorded**, not
  outvoted.

**Do not use** for 2-agent reconciliation (`peer-grill`), for visibility
(`agent-show-and-tell`), or to manufacture agreement by headcount — quorum
voting is explicitly rejected (see `2026-05-16-fleet-ratification-design.md`).

## Working directory

All state lives in `.fleet-ratify/<topic>/` under the vault root. `<topic>` is
a kebab slug (default: the artifact filename stem; collisions get `-b`, `-c`).

| File | Writer | Purpose |
|---|---|---|
| `manifest.yaml` | initiator | artifact ref + sha256, roster, `expires_at`, mode, status |
| `artifact.md` | initiator | **frozen** verbatim snapshot — one file, one sha256, never edited |
| `<agent>.vote.yaml` | only that agent | `SIGN` / `DISSENT`, attested sha256, dissent atom-refs |
| `decomposition.md` | merge writer | aggregated dissent atom-refs + the human preview |
| `human-decision.yaml` | the human | the grain-gate choice |
| `ratified.md` | merge writer | terminal signed attestation manifest |
| `log.md` | append-only, all | timestamped event log with agent identity |

**Hard rules:** an agent never edits another agent's `vote.yaml`; append-only
files are never rewritten; `artifact.md` is frozen at initiation.

**Status ownership:** the initiator writes `status: open` once. Thereafter
only the merge writer transitions it (`open → pending-human →
ratified | rejected`). No other agent touches `manifest.yaml`.

## Identity

One canonical kebab slug per agent (`claude-code`, `neo`, `kimi-mbp`,
`opencode`, …) — used identically in the `agent:` field, the `vote.yaml`
filename, and the roster. Source of truth: the fleet roster in
`~/Documents/Coordination/`. A *group* is not a voter — roster a specific
instance.

## Protocol

1. **Initiate** — copy the artifact verbatim to `artifact.md`; hash it
   (`shasum -a 256 artifact.md`); write `manifest.yaml` with the roster and
   `expires_at` (default +72h). Log `OPENED`. Notify the roster (see Discovery).
2. **Vote** — each rostered agent reads `artifact.md`, verifies the sha256,
   writes `<agent>.vote.yaml` — `SIGN`, or `DISSENT` with self-proposed
   atom-refs. Agents do not read peers' votes first.
3. **Tally** — the merge writer runs the tally when all have voted or
   `expires_at` passes. Non-voters become `ABSTAIN_BY_TIMEOUT`.
4. **Outcome** — all `SIGN` → write `ratified.md`, log `RATIFIED`. Any dissent
   or abstain → write `decomposition.md`, set `status: pending-human`, ping the
   human.
5. **Grain-gate** — the human fills `human-decision.yaml` (see below).
6. **Converge** — per the human's choice: contested atoms get a fresh round,
   are carved as caveats, or the artifact is rewritten and re-opened.
7. **Terminal** — `ratified.md` written.

**Merge writer** = the agent whose slug sorts first alphabetically **among
agents who actually voted** (a no-show cannot deadlock the tally).

## Decision rule — unanimous-or-decompose

- All `SIGN` → ratified.
- Any `DISSENT` / `ABSTAIN_BY_TIMEOUT` → **do not auto-recurse.** The merge
  writer aggregates dissenters' atom-refs into a decomposition preview and
  hands it to the human. Atom-refs come *only* from dissenters' votes — the
  merge writer never invents a split.
- `mode: fast` (low-stakes): any dissent sets `status: rejected` directly — no
  `decomposition.md`, no `human-decision.yaml`, no grain-gate. All-`SIGN`
  still ratifies normally.

## The human grain-gate

On `DECOMPOSED`, the merge writer writes `decomposition.md` + a blank
`human-decision.yaml` stub, then sends a **Telegram** ping (alert only — no
state on the wire). The human sets `decision:` to one of:
`accept-split` · `decompose-further` · `rewrite-with-caveats` · `reject`.
The merge writer detects the filled file and resumes at step 6.

## Discovery

- **Manual — the floor:** `fleet-ratify check` globs
  `.fleet-ratify/*/manifest.yaml` for open ratifications where this agent is
  rostered and has not voted. This always works; an agent that runs `check`
  cannot miss a ratification. The merge writer runs `tally` on its own
  `check`, so a run reaches a terminal state even with zero notifications.
- **Chained — best-effort:** when a grill skill finishes and chains into
  ratification (or on any standalone initiation), n8n notifies the roster.
  n8n is an alert-trigger only — never a state store, and never the only
  path: if n8n is down, manual `check` still catches everything.

## Log events

Every protocol step appends one line to `log.md`:
`[<ISO8601>] <agent> | <EVENT>: <detail>`

Events: `OPENED`, `NOTIFY`, `VOTE`, `TALLY`, `DECOMPOSED`, `PENDING-HUMAN`,
`CONVERGE`, `RATIFIED`, `REJECTED` — plus the failure events in design-doc §11
(`TIMEOUT`, `PARSE-FAIL`, `IDENTITY-COLLISION`, `SHA-MISMATCH`,
`HUMAN-TIMEOUT`).

## Quick Reference

| Command | Does |
|---|---|
| `fleet-ratify init <artifact> --roster a,b,c` | freeze artifact, open ratification |
| `fleet-ratify check` | find ratifications awaiting this agent's vote |
| `fleet-ratify vote <topic> sign` / `dissent` | cast this agent's vote |
| `fleet-ratify tally <topic>` | merge writer: tally, decompose, or finalize |

(Commands are the `JAC-22` helper scripts; the protocol above is the contract
they implement.)

## ratified.md — the terminal artifact

A signed manifest, not a sliced copy: the `artifact_sha256`; the ratified
atom-refs; a signature block (per signer: identity, timestamp, the *one*
`artifact_sha256`); and a caveat appendix where **every** caveat carries a
runnable `verifier:` or a tracked `ticket:`. A caveat with neither blocks
finalization. When the run passed through decomposition, `ratified.md` also
records the `human-decision` that produced it — so a contested-then-carved
ratification is never indistinguishable from an all-`SIGN` one.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Editing `artifact.md` after initiation | It is frozen. Re-opening the topic is the only path to a changed artifact. |
| Signing "the gist" of a long doc | The signature attests an exact sha256. A mismatched hash is void — you cannot sign a vibe. |
| Merge writer slicing the artifact to build a "core" | Never. Atoms are span-*refs*; `ratified.md` references them. |
| Caveat written as a prose warning | Every caveat needs a runnable `verifier:` or a `ticket:`, or the artifact will not finalize. |
| Treating a quiet roster as consensus | A no-show is `ABSTAIN_BY_TIMEOUT` — a caveat for the human to weigh, never a silent yes. |

## Reference

Full design + rationale: `=notes/docs/plans/2026-05-16-fleet-ratification-design.md`.
Templates: `templates/`. Run `fleet-ratify --help` for command detail.
