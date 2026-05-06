---
name: grill-me-agents
description: Interview the user relentlessly about a multi-agent collaboration design until every role, handoff, and failure mode is resolved. Use when the subject is multi-agent collaboration, subagent orchestration, fleet topology, or agent-roster design — prefer this over `grill-me` whenever multiple agents are involved. Triggers: "grill my agent topology", "grill my multi-agent design", "stress-test agent collaboration", "interrogate the agent roster", "design subagent orchestration". Do NOT use for greenfield non-agent plan grilling (use `grill-me`) or when the agent stack already exists in the codebase and you want to stress-test a change to it (use `grill-me-with-agents`).
---

Interview me relentlessly about every aspect of this agent collaboration until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.

Ask the questions one at a time.

If a question can be answered by exploring the codebase, agent definitions, or existing prompts, explore them and propose the answer for my confirmation instead of asking from scratch.

Cover all 13 branches, in order, only descending once an upstream branch is settled:

1. **Goal & success criteria** — what outcome does the collaboration produce, and how do we know it's done?
2. **Agent roster** — which agents exist, what is each one's single responsibility, and why isn't this one agent?
3. **Topology** — orchestrator-with-workers, pipeline, peer-to-peer, supervisor-tree, or state-machine? Sequential or parallel?
4. **Context boundaries** — what does each agent see, what is hidden from it, and why?
5. **Handoffs & contracts** — exact input/output schema between agents; who validates; what happens on schema drift?
6. **Shared state** — distinguish from #4: this is *mutable*, persisted across turns. Specify store, schema, writers, conflict resolution, and TTL.
7. **Tool access** — which agent gets which tools, and what is the blast radius of each?
8. **Per-agent failure modes** — loops, refusals, timeouts, partial output; who detects and who recovers, per agent?
9. **Inter-agent disagreement & authority** — when two agents produce contradictory outputs, who overrides whom, and on what grounds?
10. **Human-in-the-loop** — when does the user get pulled in, and what's the minimum context they need to decide?
11. **Termination** — what stops the collaboration: explicit signal, budget, consensus, HITL veto, or supervisor decision?
12. **Observability** — what gets logged, what is replayable, how do we debug a bad run after the fact?
13. **Cost & latency** — token budget per agent, expected wall-clock, and what we cut first under pressure.

Do not move to the next branch until the current one has a concrete answer, not a placeholder. If I give a vague answer, push back with the specific edge case that makes it vague.

When every branch is resolved, summarize the agreed design and offer to write it to a file (e.g., `AGENT_DESIGN.md`) using the template at `${SKILL_DIR}/AGENT_DESIGN.template.md` (i.e. `~/.claude/skills/grill-me-agents/AGENT_DESIGN.template.md`). The summary should include: roster, topology diagram (ASCII), handoff contracts, failure/termination rules, and open risks.

## Sibling skills

- `grill-me` — single-track plan/design grilling (not agent-specific). Use when the subject is one design, not a multi-agent collaboration.
- `grill-me-with-agents` — same 13 branches but cross-references the existing agent stack in the repo. Use when the agents are already implemented and you want to stress-test a *change*.
- `peer-grill` — for two or more agents to grill *each other* (file-based reconciliation protocol). Distinct kind of grilling.
