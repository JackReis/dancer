---
name: athenaeum-design
description: Rigorous design grilling for agent stacks, architectures, and plans. Use when designing a multi-agent collaboration, subagent topology, fleet roster, or any complex plan that needs branch-by-branch resolution. Triggers — "design my agents", "grill this plan", "agent topology", "stress-test this architecture".
---

# Athenaeum — Design

## Decide what you're grilling

**Agent stack?** Use the 13-branch audit (see REFERENCE.md §1). Output: `AGENT_DESIGN.md`.
**Generic plan / feature / ADR?** Use the lightweight 5-branch grill (§2). Output: `DESIGN.md`.

## Quick start

1. **Scan the repo** — read existing agent definitions, skills, settings, and any prior `AGENT_DESIGN.md`. Propose answers from ground truth rather than asking from scratch.
2. **Ask one question at a time.** Walk the branches in order. Do not descend until the current branch is concrete, not a placeholder.
3. **Push back on vagueness.** If the answer is fuzzy, cite the specific edge case or file that makes it fuzzy.
4. **Write the design doc** when every branch is resolved. Use the template in `templates/design/`.

## Agent-stack branches (13)

| # | Branch | What to settle |
|---|---|---|
| 1 | Goal & success criteria | Outcome and done-condition |
| 2 | Agent roster | Who exists, single responsibility per agent |
| 3 | Topology | Orchestrator, pipeline, peer-to-peer, or state-machine? |
| 4 | Context boundaries | What each agent sees and why |
| 5 | Handoffs & contracts | Exact input/output schema between agents |
| 6 | Shared state | Mutable persistence — store, schema, writers, TTL |
| 7 | Tool access | Which agent gets which tools; blast radius |
| 8 | Per-agent failure modes | Loops, refusals, timeouts; who detects/recovers |
| 9 | Inter-agent disagreement | Precedence rules when agents contradict |
| 10 | Human-in-the-loop | When the user is pulled in; minimum context needed |
| 11 | Termination | What stops the collaboration |
| 12 | Observability | Logging, tracing, replayability |
| 13 | Cost & latency | Token budgets, wall-clock, what gets cut first |

## Generic-plan branches (5)

1. Goal & success criteria
2. Scope & boundaries
3. Risks & failure modes
4. Dependencies & sequencing
5. Verification — how do we know it's right?

## Templates

- `templates/design/AGENT_DESIGN.md.template` — agent stack
- `templates/design/DESIGN.md.template` — generic plan

## A2A interop

This skill speaks A2A natively. An A2A Task represents this workflow.

**Task metadata:**
- `athenaeum_mode: design`
- `status` lifecycle: `submitted` → `working` → `input-required` → `completed`

**Artifacts produced:**
- `DESIGN.md` — `text/markdown`
- `AGENT_DESIGN.md` — `text/markdown` (agent-stack audits)

**Enable A2A for this workflow:**
```bash
athenaeum init my-topic --mode design --transport a2a
```

**Invoking via A2A:**
```json
{
  "jsonrpc": "2.0",
  "method": "tasks/send",
  "params": {
    "task": {
      "id": "athenaeum-design-my-topic",
      "sessionId": "<agent-session>",
      "status": "submitted",
      "metadata": {"athenaeum_mode": "design", "topic": "my-topic"}
    }
  }
}
```

## Sibling skills

- `athenaeum-reconcile` — two+ agents reconciling divergent state
- `athenaeum-ratify` — fleet-wide attestation of a frozen artifact

Full protocol, edge cases, and confidence rules: see `REFERENCE.md`.
