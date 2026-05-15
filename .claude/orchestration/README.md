# Orchestration — Worker-Tier Setup

This repo is a **worker-tier target** under the Arbiter orchestration topology
(see `=notes/AGENT_DESIGN.md` in the portfolio vault). Arbiter spawns isolated
CC workers against worktrees of this repo to ship Linear-ticketed work as PRs.

This directory contains the contract, settings, and bootstrap hooks that make
those workers reproducible without depending on Jack's local filesystem.

## Files

| Path | Purpose |
|------|---------|
| `WORKER-CONTRACT.md` | This repo's role under Arbiter — dispatch envelope, proof-of-work, budgets, failure modes |
| `worker-settings.json` | Minimal CC `settings.json` template for autonomous workers spawned by Hermes |
| `contracts/dispatch_envelope.schema.json` | JSON schema for `n8n → Arbiter → worker` dispatch payload |
| `contracts/proof_of_work.schema.json` | JSON schema for `worker → Arbiter` completion payload |
| `hooks/bootstrap.sh` | Worktree self-bootstrap — handles GitNexus availability hazard (branch-13 risk note) |

## Spawn protocol (Hermes → CC worker)

```bash
# 1. Hermes creates a worktree off main
git worktree add ../worktrees/<linear_id> -b worker/<linear_id> origin/main

# 2. Hermes spawns CC with minimal worker profile (no human-mode hooks)
claude code \
  --cwd ../worktrees/<linear_id> \
  --settings .claude/orchestration/worker-settings.json \
  --dispatch-envelope <dispatch_envelope.json>

# 3. Worker runs bootstrap (gitnexus index, dep install) before touching code
.claude/orchestration/hooks/bootstrap.sh
```

Workers MUST NOT reach outside their worktree. The worker-settings profile
denies the Bash patterns that would let them.

## Quickstart (humans / local dev)

```bash
# One-shot: index the repo and wire MCP for your local CC
npx gitnexus analyze --skills    # generates .claude/skills/gitnexus/ (gitignored)
npx gitnexus setup                # registers MCP for Cursor/CC/OpenCode/Codex
```

The `.mcp.json` at repo root pins gitnexus as a project-level MCP server so
that anyone cloning the repo gets the same tool surface without per-user
`gitnexus setup`.

## Logs

Per the design doc, Arbiter writes forensic per-ticket traces to
`claude/orchestration/tickets/<linear_id>/trace.jsonl`. That tree is created
on demand by Arbiter and is **not** part of this repo's source — it's runtime
state owned by the orchestrator container.
