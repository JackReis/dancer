---
name: peer-grill-with-agents
description: Two (or more) agents independently audit the SAME existing agent stack against the codebase, then reconcile via the peer-grill file-based protocol. Each agent walks the same 13-branch agent-stack audit (grill-me-with-agents) on its own, dumps a claims.yaml grounded in concrete file paths, and the disagreements get ratified or escalated. Use when the agent topology is already implemented and you need multi-agent triangulation on whether a *change* to it is sound — single-agent grilling has known blind spots, peer-grill alone has no code anchor, this combines them. Triggers — "peer-grill the agent stack", "two agents audit the topology", "stress-test our agents from two angles", "triangulate the agent design", "reconcile our reading of the stack". Do NOT use for greenfield design (use `grill-me-agents`), for single-agent code-aware grilling (use `grill-me-with-agents`), or for non-agent state reconciliation (use `peer-grill`).
---

> Flagship skill for the Arbiter orchestration package. Where `grill-me-with-agents` audits an implemented stack with one agent's lens, `peer-grill-with-agents` runs that audit through N agents in parallel and reconciles the deltas. The output is a multi-agent-ratified `AGENT_DESIGN.md` that no single model authored alone — the design has survived independent code-anchored interrogation by every peer.

This skill is the dialectic protocol at agent-design scale. It composes two existing primitives without replacing them: the **13-branch audit** from `grill-me-with-agents` (what to read in the repo, in what order) and the **file-based reconciliation protocol** from `peer-grill` (claims → diff → grill → ratify → sign-off). Read both for full mechanics; this skill describes how they fit together.

## When to invoke

- A design change is proposed against an *existing* multi-agent stack and the stakes warrant > one model's read of it.
- Two parallel sessions are working on the same agent-topology question and you suspect they're forming divergent mental models.
- A non-Claude peer (Gemini, GPT, local model) has been asked to review an agent design and you want the review to converge with the Claude perspective, not just sit alongside it.
- Authoring or amending an `AGENT_DESIGN.md` — peer-grill-with-agents produces the canonical artifact.

Do NOT invoke when:
- The agent stack doesn't exist yet (`grill-me-agents` — greenfield).
- One agent is enough — single-agent rigor is satisfied by `grill-me-with-agents`.
- The reconciliation isn't about agents (vanilla `peer-grill`).

## Setup — ask the user before any writes

1. **Topic slug** — what change or design is being grilled? e.g. `arbiter-rollout`, `hermes-demotion`, `pt-dissent-gate`. Default to `arbiter-rollout` if unspecified.
2. **Identities** — what name is *this* agent? (`claude-opus-4-7`, `gemini-2.5-pro`, `gpt-5-codex`, etc.) What identities are the peers, and how do they invoke the skill (separate session, separate machine, manual prompt)?
3. **Stack scope** — which subdirectories of `.claude/agents/`, `.claude/skills/`, `.claude/shared-agents/`, etc. are in scope? Anything outside is filtered out before diffing.
4. **Round budget** — max grilling rounds per disputed branch before `ESCALATE` (default: 3, per `peer-grill`).
5. **`poll_timeout_minutes`** — wall-clock cap on Phase 2 and Phase 5 waits (default: 30).

If a peer is non-Claude, offer to draft a one-page system-prompt summary the user can paste into that peer so it follows the same protocol. The protocol is symmetric; it does not assume Claude-on-both-sides.

## Working directory

All artifacts live in `.peer-grill/<topic>/` relative to repo root — same convention as `peer-grill`. Files (see `peer-grill` SKILL.md for full semantics):

| File | Writers | Purpose |
|---|---|---|
| `<agent>.claims.yaml` | only that agent | self-reported audit of the agent stack |
| `diff.md` | last writer (append-only) | three-bucket diff: agreed / disagreed / only-one |
| `grill-log.md` | append-only, all peers | Q&A transcript with timestamps + agent identity + branch number |
| `state.merged.yaml` | merge writer (first alphabetically) | the ratified ground truth, drives `AGENT_DESIGN.md` generation |
| `unresolved.md` | append-only, all peers | escalated disputes; both/all positions recorded |
| `signoff.md` | append-only, all peers | sha256-attested final state per peer |

Hard rules from `peer-grill` apply unchanged — never edit a peer's claims file; only the merge writer writes `state.merged.yaml`; append-only files stay append-only.

## Protocol — single thread, 7 phases

### 1. Independent audit (code-anchored dump)

Each peer walks the **13 branches** from `grill-me-with-agents` independently, citing concrete file paths from this repo. Each branch becomes one or more claims in the peer's `<agent>.claims.yaml`. The 13 branches, in order — do not descend until upstream is settled within your own audit:

1. **Goal & success criteria**
2. **Agent roster** — for each agent in `.claude/agents/` or `.claude/shared-agents/`, confirm responsibility against its frontmatter
3. **Topology** — diff the proposed change against the current topology; flag every removed/repurposed agent
4. **Context boundaries** — read each agent's `tools:` allowlist
5. **Handoffs & contracts** — find where messages cross agent boundaries today (file conventions, MCP calls, settings hooks)
6. **Shared state** — locate mutable persistence (files, MCP servers, env)
7. **Tool access** — read each agent's tool list, flag privilege creep
8. **Per-agent failure modes** — inspect hooks + error paths in `settings.json`
9. **Inter-agent disagreement & authority** — find precedence rules in prompts or orchestration code
10. **Human-in-the-loop** — locate `AskUserQuestion`, `ExitPlanMode`, confirmation gates
11. **Termination** — current stop conditions in orchestration code
12. **Observability** — logging / tracing / trace files / status endpoints already wired
13. **Cost & latency** — model assignments per agent (`model:` frontmatter)

Claim format (extends `peer-grill`'s schema with a `branch` field):

```yaml
agent: <agent-name>
session_started: <ISO8601>
scope: [<stack-paths-in-scope>]
claims:
  - id: <stable-slug>            # e.g., arbiter-port, hermes-role, pt-dissent-gate
    branch: 1..13                # which branch this claim sits in
    statement: <one sentence>
    confidence: high | medium | low
    source: <file:line | command-output | quoted-frontmatter>
    last_verified: <ISO8601>
```

**Confidence rules tighten here:** `high` requires a quoted file path + line range AND a verifying read; `medium` is "I read it but the artifact may be stale"; `low` is "I inferred this from adjacent files." If you cannot find a source for a claim within scope, the correct answer is "no claim" — do NOT invent.

**Do NOT read peer claims yet.** Independent dump is load-bearing; context leakage defeats triangulation.

### 2. Read & validate peers' claims

Poll for each peer's `<peer>.claims.yaml` per `peer-grill` Phase 2 (60s poll, `poll_timeout_minutes` cap, parse-retry on YAML failure, identity-collision check). Terminal events from `peer-grill` apply: `TIMEOUT: phase=2`, `PARSE-FAIL`, `IDENTITY-COLLISION`.

Additional check for this skill: every peer's `scope` field must match. If scopes differ, emit `SCOPE-MISMATCH: <peer>` to `grill-log.md` — the audit isn't comparable until scopes align. Pause until the user reconciles.

### 3. Diff per branch

Compute the three-bucket diff (`agreed`, `disagreed`, `only-one-knows`) and **group by branch number** in `diff.md`. Grouping matters: branch 1 (Goal) disagreements likely cascade into branch 3 (Topology); resolve upstream first.

If a peer's diff disagrees with yours (different bucket assignment for the same id), that's itself a disagreement — log it in `grill-log.md` and resolve before grilling claims. Silent-drop bugs are the most expensive failure mode of this protocol.

### 4. Grill loop — branch-ordered

Run the `peer-grill` grill loop, but iterate **branch-by-branch in 1→13 order**. Within a branch, iterate claims by id alphabetically.

Per-question rigor floor (stricter than `peer-grill`):

- Every question must cite the specific file path or frontmatter field the asker doubts.
- Every answer must quote ≤ 80 characters from a verifiable source. "Trust me, I read it" is grounds for another round.
- For disagreements where one peer claims `high` and the other `low`: the `high` claim must produce its source on first request, OR drop to `medium` immediately. Confidence asymmetry without sourcing is a tell.
- Ratification (`RATIFY: <claim-id> | <agreed-statement>`) follows `peer-grill` semantics. Both/all peers' statements must match exactly modulo whitespace.

Round budget exhaustion → `ESCALATE: <claim-id>` to `unresolved.md`. Protocol continues; only that claim is finalized as unresolved.

### 5. Merge — driven by branch order

The merge writer (peer whose name sorts first alphabetically) waits for every claim to be ratified or escalated, then overwrites `state.merged.yaml`. Schema:

```yaml
topic: <topic>
ratified_at: <ISO8601>
peers: [<agent-a>, <agent-b>, ...]
stack_scope: [<paths>]
claims:
  - id: <id>
    branch: 1..13
    statement: <agreed statement>
    sources: [<from agent-a>, <from agent-b>, ...]   # all sources preserved
```

Non-writer peers poll for the file's appearance per `peer-grill` Phase 5 (`TIMEOUT: phase=5` on overrun).

### 6. Sign-off

Per `peer-grill` Phase 6: LF-normalize `state.merged.yaml`, compute sha256, append a signoff with attestation. Mismatch handling, supersession, and `INTEGRITY-FAIL` semantics carry over unchanged.

### 7. Author AGENT_DESIGN.md

Once all peers have sign-offs and hashes converge, the merge writer generates `AGENT_DESIGN.md` from `state.merged.yaml`, organizing by the 13-branch ordering. Template: `~/.claude/skills/grill-me-agents/AGENT_DESIGN.template.md` if present; otherwise mirror the structure of existing `AGENT_DESIGN.md` files in the repo (read the most recent for style).

The generated `AGENT_DESIGN.md` includes a footer:

```markdown
*Peer-ratified by: <agent-a>, <agent-b>, ...*
*State sha256: <hex from signoff.md>*
*Reconciliation artifacts: .peer-grill/<topic>/*
```

This footer is non-negotiable — it's the audit trail. Removing it severs the design from its provenance.

## Multi-peer (3+)

`peer-grill`'s pairwise-chain extension applies: run A↔B, then merged↔C, document chain order in `grill-log.md`. Each pairwise reconciliation produces a `state.merged.<n>.yaml` to feed the next pair. Star topologies remain out of scope.

For agent-stack audits, prefer 2-3 peers across model families (e.g., Opus + Gemini + GPT) over 3+ Claude sessions — same-family agents converge on shared blind spots.

## Guardrails specific to agent audits

- **The codebase is the tiebreaker.** When peers disagree and neither can produce a stronger source, re-read the file together (both peers cite the same `file:line-range` in their next round). The repo wins; agent recollection does not.
- **Frontmatter beats prose.** A claim about an agent's tools sourced from `tools:` allowlist beats a claim sourced from the prose body of the agent's prompt.
- **`AGENT_DESIGN.md`'s `supersedes:` field is load-bearing.** When generating a new `AGENT_DESIGN.md`, the prior design (if any) must be in the `supersedes:` field with its sha256. Otherwise the audit trail breaks at the design-doc boundary.
- **Don't peer-grill yourself.** If both peers are Claude sessions on the same machine sharing context, the protocol degrades into single-agent grilling with extra steps. Different machine, different model, or different user-driven session — never shared transcript history.

## Sibling skills

- `grill-me-with-agents` — single-agent, code-aware audit of an existing stack. The 13-branch audit lives there; this skill composes it.
- `grill-me-agents` — greenfield agent design (codebase-blind).
- `peer-grill` — non-agent state reconciliation; this skill's protocol substrate.
- `grill-me` — single-track plan grilling, not agent-specific.

## Provenance

This skill was authored as the flagship for the Arbiter orchestration package — the Arbiter design itself (`AGENT_DESIGN.md` at vault root) was produced by a single-agent run of `grill-me-with-agents`, and the natural next-iteration upgrade is multi-agent ratification. Lineage: `grill-me` → `grill-me-with-agents` → `peer-grill` → this skill. Each step adds rigor without discarding the prior level.
