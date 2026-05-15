---
name: grill-me-with-agents
description: Code-aware variant of grill-me-agents — interrogates a multi-agent design while continuously cross-referencing existing agent definitions, skills, prompts, and tool configs in the repo. Use ONLY when the agent stack is already implemented in the repo and you want to stress-test a *change* to it (versus designing from scratch — use `grill-me-agents` for greenfield). Triggers: "grill the existing agent stack", "stress-test the agent stack", "grill the implemented agents", "audit the agent topology against code". Do NOT use for greenfield agent design (use `grill-me-agents`) or for two agents grilling each other (use `peer-grill`).
---

Interview me relentlessly about every aspect of the proposed agent collaboration until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies one-by-one. For each question, provide your recommended answer.

Ask the questions one at a time.

Before asking any branch, scan the repo for ground truth and cite what you found. Look in (in priority order):

- `.claude/agents/`, `.claude/shared-agents/` — existing agent definitions
- `.claude/skills/`, `.claude/shared-skills/` — skills the agents may invoke
- `.claude/settings.json`, `.claude/settings.local.json` — permissions, hooks, env
- `.claude/AGENT-STACK.md`, `CLAUDE.md`, any `AGENT_DESIGN.md` — declared topology
- `.github/workflows/` — CI hooks that gate or trigger agent runs
- Any orchestration code referencing the Agent SDK or MCP servers

If a branch can be answered from those sources, propose the answer for my confirmation rather than asking from scratch. Quote the file and line so I can verify.

If the codebase contradicts what I tell you, surface the contradiction and ask which is canonical before proceeding.

Cover the same 13 branches as `grill-me-agents`, in order, only descending once an upstream branch is settled:

1. **Goal & success criteria**
2. **Agent roster** — for each existing agent, confirm responsibility against its definition file
3. **Topology** — diff the proposed topology against the current one; flag every removed or repurposed agent
4. **Context boundaries** — check actual `tools:` allowlists in agent frontmatter
5. **Handoffs & contracts** — locate where messages cross agent boundaries today
6. **Shared state** — find where mutable state actually persists (files, MCP servers, env); distinguish from #4
7. **Tool access** — read each agent's tool list and flag privilege creep
8. **Per-agent failure modes** — check existing hooks and error paths in settings.json for each agent
9. **Inter-agent disagreement & authority** — find any precedence rules in agent prompts or orchestration code
10. **Human-in-the-loop** — locate `AskUserQuestion`, `ExitPlanMode`, and confirmation gates
11. **Termination** — find current stop conditions in orchestration code
12. **Observability** — check for logging/tracing infra already wired up
13. **Cost & latency** — note model assignments per agent (`model:` frontmatter)

Do not move to the next branch until the current one has a concrete answer, not a placeholder. If I give a vague answer, push back with the specific file or edge case that makes it vague.

When every branch is resolved, summarize the agreed design and offer to write it to `AGENT_DESIGN.md` using the template at `~/.claude/skills/grill-me-agents/AGENT_DESIGN.template.md` (sister-skill template, intentionally shared). Include: roster (with file paths), topology diagram (ASCII), handoff contracts, failure/termination rules, observability hooks, and a diff against the previous design if one existed.

## Sibling skills

- `grill-me-agents` — same 13 branches but greenfield (codebase-blind). Use when designing a new agent stack from scratch.
- `grill-me` — single-track plan/design grilling (not agent-specific).
- `peer-grill` — for two or more agents to grill *each other* (file-based reconciliation protocol).
