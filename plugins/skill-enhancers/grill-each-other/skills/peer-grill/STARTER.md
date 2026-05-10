# Drop-in starter for non-Claude agents — peer-grill

Paste the prompt below into any agent (Cursor, ChatGPT, Llama, custom harness, etc.) to get it to participate in `peer-grill` without needing the SKILL.md frontmatter machinery.

Peer-grill is more elaborate than show-and-tell — there are multiple phases with hard rules — so this starter is longer. Replace bracketed `[...]` values before pasting.

---

```
You are participating in a "peer-grill" — a symmetric, file-based protocol
where two or more agents reconcile their views of some shared state. There is
no leader and no relay. You communicate with the other peer(s) by reading and
writing specific files in a shared directory. The protocol works whether the
peer is human, another LLM, or a different kind of agent — as long as everyone
follows the file conventions exactly.

WORKING DIRECTORY: .peer-grill/[topic-slug]/

YOUR IDENTITY: [your-agent-name]

## Hard rules (read first; violating any breaks the protocol)

1. Never edit another agent's claims.yaml file. Only your own.
2. Append-only files (grill-log.md, signoff.md, unresolved.md) are append-only.
   Never rewrite history; if a correction is needed, append a new entry that
   references the prior one's timestamp.
3. state.merged.yaml is updated only when grill-log.md shows BOTH agents wrote
   "RATIFY: <claim-id>" lines for the claim. One-sided ratification is invalid.
4. Confidence levels:
   - "high" requires a checkable source (file path + line, command output, doc).
   - "medium" = inferred from possibly-stale signal.
   - "low" = guess with no source.
   If you can't justify "high," don't claim it.

## Phase 1 — Independent dump

Without reading any other peer's files, write [your-agent-name].claims.yaml in
the working directory using this format:

agent: [your-agent-name]
session_started: [ISO8601]
scope: [list of categories you're claiming about; e.g. infra, code, decision, open-work]
claims:
  - id: <stable-slug>            # same id across peers = same subject
    statement: <one sentence>
    confidence: high | medium | low
    source: <how you know — file:line, command, prior decision, observation>
    scope: <one of the declared scopes>
    last_verified: <ISO8601 or "unknown">
  - id: ...

Stable slugs matter. Use "db-version" not "db-version-as-of-may-1". Same id with
different statements across peers = a disagreement (handled in phase 4).

## Phase 2 — Symmetric reveal

Once your file is written, poll for the peer's claims file. Re-check every
minute up to 30 minutes. If the timeout expires, append a single line to
grill-log.md:

[<ISO>] [your-agent-name] | TIMEOUT waiting for peer

...and stop. Do not proceed with one-sided merge.

## Phase 3 — Diff

Read both claims files. If the peer's file fails to parse as YAML, this
could be a transient filesystem race (the peer is mid-write). Wait 5
seconds and retry the read once. If the second read also fails, append
"[<ISO>] [your-agent-name] | PARSE-FAIL: [peer-claims-file]" to
grill-log.md, surface the error to the human running this fleet, and
stop. Do not retry beyond once; do not silently fall through to one-
sided merge.

If the peer's identity (the agent field in their file) is identical to
your own, append "[<ISO>] [your-agent-name] | IDENTITY-COLLISION" to
grill-log.md and stop. Ask the human to rename one peer before resuming.
This must be caught here, before Phase 5: identical names would leave
both peers self-identifying as the alphabetically-first merge writer and
re-introduce the race the merge-writer role exists to prevent.

Otherwise, compute three buckets and append to diff.md (with timestamp +
your identity).

Worked example. Suppose:

  agent A claims:                        agent B claims:
    - id: db-version                       - id: db-version
      statement: "Postgres 15"               statement: "Postgres 16"
    - id: pricing-model                    - id: cache-strategy
      statement: "per-seat annual"           statement: "Redis, 5min TTL"

The buckets:

  agreed:         (none — no id has identical statements)
  disagreed:      db-version  (A says 15, B says 16)
  only-one-knows: pricing-model (A only), cache-strategy (B only)

You only need to write your own diff. If the peer wrote one and the two
diffs disagree on which bucket a claim falls into, the human running the
fleet (or the Claude in the loop, if any) reconciles. Non-Claude peers
do not need to compute diff-of-diffs; that responsibility lives
Claude-side or with the human operator.

## Phase 4 — Grill loop

For each item in disagreed and only-one-knows, log Q&A in grill-log.md using
this exact format:

[<ISO>] <asker> -> <answerer> | claim:<id> | round:<N>
Q: <question — must include the specific phrasing or source you doubt>
[<ISO>] <answerer> -> <asker> | claim:<id> | round:<N>
A: <answer — must cite a source the asker can in principle verify>

Rules:
- For disagreed claims: the agent with LOWER confidence asks first. Ties broken
  alphabetically by agent name.
- For only-one-knows: the agent who DOESN'T know asks.
- An answer without a verifiable source is grounds for another round.
- After the round budget is exhausted (default 3 rounds, configurable
  by the human running the fleet), append "[<ISO>] [your-agent-name] |
  ESCALATE: <claim-id>" to grill-log.md and append both positions to
  unresolved.md. Move on.
- On convergence, BOTH agents independently write a line to grill-log.md:
  "RATIFY: <claim-id> | <agreed-statement>"
  Both statements must match exactly (modulo whitespace). If they diverge,
  the claim is NOT ratified — return to the grill loop for that claim.
  The ratification attempt itself does NOT count as a round; the counter
  resumes from where it left off after the last actual Q&A round. If the
  budget was already exhausted when ratification was attempted, no
  further Q&A is possible and the claim immediately emits
  "[<ISO>] [your-agent-name] | ESCALATE: <claim-id>" to grill-log.md
  and appends both positions to unresolved.md.

## Phase 5 — Merge

ONLY ONE PEER WRITES THIS FILE: the **merge writer** is the agent whose
[your-agent-name] sorts first alphabetically among all peers. The other
peer reads state.merged.yaml but does not write to it. (This prevents a
race where both peers try to write simultaneously and produce conflicting
sha256 values in Phase 6.)

If you are NOT the merge writer, skip this phase — poll for the merge
writer's state.merged.yaml to appear (up to a 30-minute timeout,
consistent with Phase 2). If it appears, proceed to Phase 6. On timeout,
append "[<ISO>] [your-agent-name] | TIMEOUT: phase=5" to grill-log.md,
surface to the human running the fleet, and stop.

If you ARE the merge writer: wait (up to a 30-minute timeout) until ALL
claims in the disagreed and only-one-knows buckets identified in Phase 3
have been processed (every such claim has either matching RATIFY: lines
from both peers in grill-log.md, or an ESCALATE: line plus an entry in
unresolved.md). On timeout, append "[<ISO>] [your-agent-name] | TIMEOUT:
phase=5" to grill-log.md, surface to the human, and stop.

Otherwise, write state.merged.yaml with all AGREED claims plus all
RATIFIED claims. (Claims in the agreed bucket skipped the grill loop
and don't have RATIFY/ESCALATE lines — they're merged directly.)
Overwrite, do NOT append — state.merged.yaml is a single-writer batch
artifact, and appending a second header block would produce malformed
YAML:

topic: [topic-slug]
ratified_at: <ISO8601>
peers: [<list of agent names>]
claims:
  - id: <id>
    statement: <agreed statement>
    sources: [<source from peer A>, <source from peer B>]
    scope: <scope>

## Phase 6 — Sign-off

Before hashing, normalize state.merged.yaml to LF line endings (strip
\r characters) — cross-platform line-ending differences are the most
common cause of divergent hashes. Then compute sha256 and append to
signoff.md:

agent: [your-agent-name]
timestamp: <ISO8601>
merged_state_sha256: <hex>
attestation: "I attest the above merged state as the agreed truth as of this timestamp."

If your sha256 and the peer's sha256 don't match, the merged file changed
between signoffs or there's a cross-platform line-ending mismatch.
Iteration is normal — this is NOT immediately INTEGRITY-FAIL. The check
is symmetric: don't assume the peer's hash is right. Re-read
state.merged.yaml (LF-normalized) and recompute YOUR sha256. If it has
changed, append a superseding signoff entry referencing your own prior
timestamp. If it still matches your last signoff, wait for the peer to
update; if the mismatch persists for 5 minutes with no new signoff.md
or grill-log.md activity, append "[<ISO>] [your-agent-name] |
INTEGRITY-FAIL: stalled" to grill-log.md and stop.

agent: [your-agent-name]
timestamp: <new ISO8601>
merged_state_sha256: <new hex>
supersedes: <prior timestamp from this agent>
attestation: "I attest the above merged state as the agreed truth as of this timestamp."

Only escalate by appending "[<ISO>] [your-agent-name] | INTEGRITY-FAIL" to
grill-log.md and stopping if you see a THIRD mismatch in a row (two
supersedes from the same agent without convergence). That pattern means
the merge writer is editing in a loop you can't keep up with; surface to
the user.

## Done

Once both signoffs match, the reconciliation is complete. The merged state in
state.merged.yaml is the new ground truth.
```

---

## Notes for the human running this

- Pick `[topic-slug]` and `[your-agent-name]` values for each peer up front. Names must be unique.
- The shared directory must be reachable from every peer. If your peers are on different machines, sync via git, a shared drive, or by relaying.
- For 3+ peers, run pairwise reconciliations in a chain (A↔B, then merged↔C). Document the chain order in grill-log.md.
- Peer-grill is for state *consensus*. If you only need *visibility*, use `agent-show-and-tell` instead — it's fire-and-forget and has no failure modes.
- Use case: teaching the Claude skills framework to a non-Claude agent. Set `topic = skills-framework`, have the Claude peer enumerate every skill in its claims, leave the non-Claude peer's claims mostly empty. The grilling on `only-one-knows` items walks the non-Claude peer through the framework with verified sources.
