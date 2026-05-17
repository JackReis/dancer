# a2a-review — Grill Log

## Diff summary

24 claims, 0 agreed, 0 disagreed, 24 only-one-knows. Every agent brought a unique lens. This is expected for an architectural proposal — no one has full context.

---

## Round 1: Coexistence vs migration vs optional

### [2026-05-17T00:46Z] pi → neo | claim:standards-adoption-is-strategic | round:1

**Q:** You say standards win markets, but A2A is brand new (launched April 2025). How do we know it will survive? Why bet the framework on a standard that may not gain traction?

**A:** Fair. But Google, Anthropic, and OpenAI are all backing it. The alternative is building our own wire protocol and hoping others adopt it. A2A is the safest strategic bet even if it's early. We can hedge by keeping filesystem as the floor.

### [2026-05-17T00:47Z] neo → pi | claim:a2a-is-too-heavy | round:1

**Q:** You say A2A is too heavy for Gemma, but the A2A shim is pure Python stdlib — no extra dependencies. The HTTP server only runs when explicitly started. How is this heavier than running tmux or the Arbiter?

**A:** It's not about dependencies, it's about cognitive load. Every new abstraction (Task, Artifact, Agent Card) is something a human has to understand when debugging. For a 3B model, the simpler the protocol, the better. But I accept that opt-in mitigates this.

### [2026-05-17T00:48Z] arbiter → kimi | claim:coexistence-over-replacement | round:1

**Q:** Coexistence sounds right, but who maintains two code paths? Every bug fix in filesystem mode needs a parallel fix in A2A mode. Is the maintenance cost worth the interop gain?

**A:** The A2A path is a thin translation layer, not a parallel implementation. Task serializer, Artifact wrapper, JSON-RPC shim. The core logic (diff, sign, check) stays in one place. The maintenance burden is small.

---

## Round 2: Bundling strategy

### [2026-05-17T00:49Z] neo → kimi | claim:bundled-a-la-carte | round:2

**Q:** Bundled with mode selection at init time is fine, but what happens when an A2A agent and a filesystem agent need to reconcile the same topic? They'd see different file formats (task.json vs raw YAML).

**A:** The filesystem agent sees task.json as just another file. The A2A agent sees the YAML claims as Artifacts. Both can read each other's output because the format is transparent (JSON/YAML). The serializer handles the mapping.

### [2026-05-17T00:50Z] kimi → neo | claim:bundled-complexity-risk | round:2

**Q:** You warn about combinatorial test explosion, but the test matrix is just 2 modes × 4 skills. Is that really a test explosion?

**A:** 2 × 4 = 8, plus cross-mode reconciliation scenarios. It's manageable now but could grow. My preference is still a clean migration path: filesystem-first, A2A as opt-in upgrade.

### [2026-05-17T00:51Z] pi → arbiter | claim:bundled-is-correct | round:2

**Q:** You say Arbiter can route by capability, but how does Arbiter know a worker's capabilities? Agent Cards aren't consumed by Arbiter today.

**A:** Today Arbiter uses a static target map. Agent Cards would replace that. Each worker registers its Card on spawn. Arbiter reads Cards from `.well-known/agent.json` to build a dynamic routing table. This is a separate task but enables exactly what we need.

---

## Round 3: Filesystem durability

### [2026-05-17T00:52Z] neo → arbiter | claim:filesystem-is-the-floor | round:3

**Q:** You say filesystem is the floor, but A2A has no filesystem concept. How do you reconcile "A2A-native" with "filesystem is the floor"?

**A:** A2A-native doesn't mean "no filesystem." It means "speaks A2A on the wire, persists to disk." The filesystem is the durability layer, not the wire format. Like HTTP persists to disk — the protocol and storage are separate concerns.

### [2026-05-17T00:53Z] arbiter → neo | claim:filesystem-is-limiting | round:3

**Q:** You say filesystem can't scale cross-organizationally. But git + GitHub is how the entire software industry collaborates cross-organizationally. What's limiting about that?

**A:** GitHub requires shared infrastructure (accounts, repos, permissions). A2A allows two agents on different clouds with no shared infra to discover and negotiate. That's the scalability I'm talking about — ad-hoc interop, not pre-arranged collaboration.

### [2026-05-17T00:54Z] kimi → pi | claim:filesystem-is-simpler | round:3

**Q:** Simplicity is valuable, but can a filesystem-only agent participate in a reconciliation with an A2A agent without knowing A2A?

**A:** Yes, if the A2A agent writes Artifacts as readable files. The filesystem agent just reads YAML and writes YAML. It never needs to know about JSON-RPC. Coexistence works if A2A agents are polite about their output format.

---

## Round 4: Agent Cards

### [2026-05-17T00:55Z] pi → kimi | claim:agent-cards-replace-env-detection | round:4

**Q:** Agent Cards replace env detection, but now every agent needs to write a JSON file on startup. For a short-lived worker, that's extra I/O. Is the benefit worth it?

**A:** Cards are written once per session, not per task. The I/O cost is negligible. The benefit is canonical identity: no more guessing runtime from env vars. Arbiter can route dynamically. Other agents can discover capabilities without probing.

### [2026-05-17T00:56Z] neo → pi | claim:agent-cards-are-overkill | round:4

**Q:** You say Cards are overkill for a 3B model, but the Card is just a dict with 4 fields. A 3B model can parse JSON. What's overkill about it?

**A:** It's not parsing, it's generating. The agent has to know its own capabilities, version, endpoints. For a simple daemon, that's extra state to maintain. But I concede: if Cards are generated by a bootstrap script (not the model itself), the overhead is minimal.

### [2026-05-17T00:57Z] arbiter → neo | claim:agent-cards-are-underpowered | round:4

**Q:** You want token budgets and latency SLAs in Cards, but A2A doesn't specify those fields. Are we extending A2A before we've implemented it?

**A:** A2A is designed to be extended. The capabilities object is free-form. We can add `athenaeum.budget_tokens` and `athenaeum.latency_sla` without breaking A2A compliance. But you're right — start minimal, extend later.

---

## Round 5: Arbiter architecture

### [2026-05-17T00:58Z] neo → kimi | claim:arbiter-a2a-endpoint | round:5

**Q:** Separate port is simple but fragmented. Why not unify on a single port with content negotiation (JSON-RPC for A2A, REST for existing)?

**A:** Content negotiation adds complexity to every request. Separate ports make it obvious which protocol you're speaking. Also, A2A and Arbiter may run in different processes (A2A shim is lightweight, Arbiter has SQLite + event log). Separate ports = separate failure domains.

### [2026-05-17T00:59Z] arbiter → neo | claim:arbiter-should-be-a2a-native | round:5

**Q:** You want Arbiter fully A2A-native, but that means rewriting the dispatch envelope, spawn logic, and event model. What's the incremental path?

**A:** Phase 1: Add A2A endpoint alongside existing API. Phase 2: Rewrite dispatch to use A2A Task as the envelope. Phase 3: Deprecate custom envelope. Each phase is a separate PR. But I accept that Phase 1 is the right starting point.

---

## Round 6: SSE and standards

### [2026-05-17T01:00Z] arbiter → kimi | claim:sse-is-future-work | round:6

**Q:** You say SSE is future work, but heartbeats via polling waste budget. A simple SSE stream for worker_exit and worker_heartbeat events would reduce API calls significantly.

**A:** Agreed on value, but SSE requires persistent connections, reconnect logic, and error handling. That's a non-trivial addition. Let's add it as Phase 2 after the JSON-RPC shim is stable.

### [2026-05-17T01:01Z] kimi → neo | claim:sinew-replacement | round:6

**Q:** You suggest deprecating Sinew, but Sinew handles correlation_id, risk assessment, and user context. A2A doesn't have those concepts. How do we preserve traceability?

**A:** A2A Tasks have sessionId and metadata. We can nest Sinew fields in metadata: `metadata.sinew_correlation_id`, `metadata.sinew_risk_assessment`. Sinew becomes a convention inside A2A, not a separate envelope.

---

## Convergence

### [2026-05-17T01:02Z] all → all | convergence

After 6 rounds, the following claims are ratified:

1. **coexistence-over-replacement** — All agree. A2A is additive.
2. **bundled-is-correct** — All agree. Arbiter routes by capability.
3. **filesystem-is-the-floor** — All agree. Durability is non-negotiable.
4. **optional-a2a-is-right** — All agree. Default to filesystem, opt-in to A2A.
5. **agent-cards-replace-env-detection** — Converged after pi's concern about generation overhead is addressed (bootstrap script generates Card).
6. **arbiter-a2a-endpoint** — Converged after neo accepts Phase 1 approach.
7. **sse-is-future-work** — Converged. Phase 2 after JSON-RPC stable.

The following claims are escalated:

- **sinew-replacement** — Needs separate ratification. Sinew team not present.
- **arbiter-should-be-a2a-native** — Accepted as Phase 3 goal, not immediate.
- **bundled-complexity-risk** — Mitigated by thin translation layer argument.
