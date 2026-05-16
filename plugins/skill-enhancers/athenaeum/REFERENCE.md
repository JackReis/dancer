# Athenaeum — Reference

Deep protocol docs for the three Athenaeum skills. Agents should read the relevant section only when executing that mode, not during skill selection.

---

## §1 Agent-stack audit (13 branches)

Branch ordering is load-bearing. Resolve upstream before descending.

**1. Goal & success criteria** — What outcome does the collaboration produce, and how do we know it's done?

**2. Agent roster** — For each agent in `.claude/agents/` or `.claude/shared-agents/`, confirm responsibility against its frontmatter. Why isn't this one agent?

**3. Topology** — Diff the proposed topology against the current one. Flag every removed or repurposed agent. Orchestrator-with-workers, pipeline, peer-to-peer, supervisor-tree, or state-machine? Sequential or parallel?

**4. Context boundaries** — What does each agent see, what is hidden, and why? Check actual `tools:` allowlists in agent frontmatter.

**5. Handoffs & contracts** — Exact input/output schema between agents; who validates; what happens on schema drift? Locate where messages cross agent boundaries today.

**6. Shared state** — Mutable persistence across turns. Specify store, schema, writers, conflict resolution, and TTL. Distinguish from context boundaries (#4).

**7. Tool access** — Which agent gets which tools, and what is the blast radius of each? Flag privilege creep.

**8. Per-agent failure modes** — Loops, refusals, timeouts, partial output. Who detects and who recovers, per agent? Inspect hooks + error paths in `settings.json`.

**9. Inter-agent disagreement & authority** — When two agents produce contradictory outputs, who overrides whom, and on what grounds? Find precedence rules in prompts or orchestration code.

**10. Human-in-the-loop** — When does the user get pulled in, and what's the minimum context they need to decide? Locate `AskUserQuestion`, `ExitPlanMode`, confirmation gates.

**11. Termination** — What stops the collaboration: explicit signal, budget, consensus, HITL veto, or supervisor decision? Find current stop conditions in orchestration code.

**12. Observability** — What gets logged, what is replayable, how do we debug a bad run after the fact? Check for logging/tracing infra already wired up.

**13. Cost & latency** — Token budget per agent, expected wall-clock, and what we cut first under pressure. Note model assignments per agent (`model:` frontmatter).

### Code-anchored confidence rules

- `high` — quoted file path + line range AND a verifying read.
- `medium` — read it, but artifact may be stale.
- `low` — inferred from adjacent files.
- No source found → no claim. Do not invent.

### Frontmatter beats prose
A claim about an agent's tools sourced from `tools:` allowlist beats a claim sourced from the prose body of the agent's prompt.

---

## §2 Generic-plan audit (5 branches)

1. **Goal & success criteria** — Outcome and done-condition.
2. **Scope & boundaries** — What's in, what's out, and why.
3. **Risks & failure modes** — What can go wrong, and what's the mitigation?
4. **Dependencies & sequencing** — What must happen before what, and what's parallelizable?
5. **Verification** — How do we know it's right? Tests, review gates, metrics?

---

## §3 Reconcile — formal mode protocol

### Working directory

`.athenaeum/<topic>/` relative to repo root.

| File | Writers | Purpose |
|---|---|---|
| `<agent>.claims.yaml` | only that agent | self-reported state dump |
| `diff.md` | last writer (append-only) | agreed / disagreed / only-one |
| `grill-log.md` | append-only, all | Q&A transcript with timestamps |
| `state.merged.yaml` | merge writer (first alphabetically) | converged ground truth |
| `unresolved.md` | append-only, all | escalated disputes |
| `signoff.md` | append-only, all | sha256 attestation |

**Hard rules:** never edit another agent's `claims.yaml`; only merge writer writes `state.merged.yaml`; append-only files stay append-only.

### Terminal events

| Event | Trigger | Phase | Action |
|---|---|---|---|
| `TIMEOUT: phase=<n>` | Poll exhausts `poll_timeout_minutes` | 2, 5 | append; surface; stop |
| `PARSE-FAIL: <file>` | YAML parse fails twice, 5s apart | 2 | append; surface; stop |
| `IDENTITY-COLLISION` | Peer's `agent` equals `<self>` | 2 | append; surface; stop |
| `ESCALATE: <id>` | Round budget exhausted | 4 | append to `unresolved.md`; continue |
| `INTEGRITY-FAIL: <reason>` | Sign-off won't converge | 6 | append; surface; stop |

### Confidence rules (claims)

- `high` — checkable source (file path + line, command output, signed doc).
- `medium` — inferred from X, but X may be stale.
- `low` — think it's true, no source.

### Ratification

Both peers must independently write `RATIFY: <claim-id> | <agreed-statement>` to `grill-log.md`. Statements must match exactly modulo whitespace. If they diverge, return to grill loop (does not count as a round). If budget already exhausted, `ESCALATE`.

---

## §4 Reconcile — quick mode

Skip SHA-256 sign-offs and round budgets. Still:
- Independent dumps.
- Three-bucket diff.
- Grill loop with at least one round per disputed claim.
- `state.merged.yaml` written by merge writer.
- `unresolved.md` for items that won't converge.

Verbal agreement is sufficient. The goal is convergence, not cryptographic proof.

---

## §5 Multi-peer reconciliation (3+)

Run pairwise in a chain: A↔B, then merged↔C. Document chain order in `grill-log.md`. Each pairwise run produces `state.merged.<n>.yaml` to feed the next pair. Star topologies are out of scope.

For agent-stack audits, prefer 2–3 peers across model families (Opus + Gemini + GPT) over 3+ Claude sessions — same-family agents share blind spots.

---

## §6 Reconcile guardrails

- **The codebase is the tiebreaker.** When peers disagree and neither can produce a stronger source, re-read the file together. The repo wins; agent recollection does not.
- **Don't peer-grill yourself.** If both peers are Claude sessions on the same machine sharing context, the protocol degrades into single-agent grilling with extra steps. Different machine, different model, or different user-driven session.
- **Never silently accept a one-sided claim.** `only-one-knows` must be grilled at least once.
- **Never rewrite append-only files.** Append a superseding entry referencing the old timestamp.
- **Don't invent claims.** Empty scope is correct if that's the truth.

---

## §7 Ratify protocol (full)

### Files

| File | Writer | Purpose |
|---|---|---|
| `manifest.yaml` | initiator | artifact ref + sha256, roster, expires_at, mode, status |
| `artifact.md` | initiator | frozen verbatim snapshot — NEVER edited after init |
| `<agent>.vote.yaml` | only that agent | SIGN / DISSENT, attested sha256, dissent atom-refs |
| `decomposition.md` | merge writer | aggregated dissent atom-refs + human preview |
| `human-decision.yaml` | human | grain-gate choice |
| `ratified.md` | merge writer | terminal signed attestation manifest |
| `log.md` | append-only, all | timestamped event log |

**Status ownership:** initiator writes `status: open` once. Thereafter only the merge writer transitions it (`open → pending-human → ratified | rejected`).

### Merge writer

The agent whose slug sorts first alphabetically **among agents who actually voted**. Determined at tally time, not reserved. Any rostered agent that sees a complete roster (or passed `expires_at`) on its `check` may compute the merge writer and, if it is itself, run the tally.

### Grain-gate decisions

- `accept-split` — ratify unanimous atoms now; contested go to fresh ratification.
- `decompose-further` — split a named contested atom again before deciding.
- `rewrite-with-caveats` — ratify whole artifact with contested atoms as caveats (each needs `verifier:` or `ticket:`).
- `reject` — end run; no `ratified.md`.

### Re-opening

If the artifact is rewritten and re-opened, the new manifest carries `supersedes: <old-topic>`. The old topic is not deleted; the chain is auditable.

---

## §8 Ratify common mistakes

| Mistake | Fix |
|---|---|
| Editing `artifact.md` after initiation | Frozen. Re-open as new topic with `supersedes`. |
| Signing "the gist" of a long doc | Signature attests exact sha256. Mismatched hash = void. |
| Merge writer slicing artifact to build "core" | Never. Atoms are span-refs; `ratified.md` references them. |
| Caveat as prose warning | Every caveat needs `verifier:` or `ticket:`, or artifact blocks finalization. |
| Quiet roster = consensus | No-show is `ABSTAIN_BY_TIMEOUT` — caveat for human, never silent yes. |

---

## §9 Log events

Every protocol step appends one line to `log.md`:
`[<ISO8601 UTC>] <agent> | <EVENT>: <detail>`

Events: `OPENED`, `NOTIFY`, `VOTE`, `TALLY`, `DECOMPOSED`, `PENDING-HUMAN`, `CONVERGE`, `RATIFIED`, `REJECTED`.

Failure events: `TIMEOUT`, `PARSE-FAIL`, `IDENTITY-COLLISION`, `SHA-MISMATCH`, `HUMAN-TIMEOUT`.
