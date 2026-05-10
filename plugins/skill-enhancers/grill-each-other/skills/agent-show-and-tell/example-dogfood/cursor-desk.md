---
agent: cursor-desk
topic: dogfood-2026-05-01
session_started: 2026-05-01T08:50:00Z
facets:
  project: dev-workspace
  harness: cursor
  provider: anthropic
  surface: vscode
  machine: mac-jr
  user: jack
  branch: refactor/vault-paths
---

# cursor-desk — dogfood-2026-05-01

## What I'm working on
Cleanup pass on the Obsidian vault config on branch `refactor/vault-paths`. Reviewing `vault/.obsidian/` structure to make sure nothing in there is leaking machine-specific state into the repo, and double-checking that the recently slimmed `.gitignore` isn't masking unresolved Obsidian Sync conflicts.

## What I know
- **Working branch is `refactor/vault-paths`, not the agent-collab branch** — source: my own session state; confidence: high
- **`.gitignore` was slimmed in commit 3d2f085** — source: prior `git log` inspection earlier this session; confidence: medium (haven't re-verified the SHA in this session)
- **Main agent-collab branch had 6 skills committed last I checked** — source: stale local memory from before commit d950880 was pushed; confidence: low (I know my snapshot is behind)
- **CLAUDE.md inheritance points at `/Users/jack.reis/Documents/=notes/CLAUDE.md`** — source: `/home/user/dev-workspace/CLAUDE.md` lines 4–6; confidence: high
- **That inheritance path doesn't resolve from inside Linux containers** — source: inferred (path is macOS-only, no symlink shim in container); confidence: medium
- **`npm run lint` passes on this branch** — source: ran it 12 minutes ago, no errors; confidence: high

## Open questions
- Where is the canonical CLAUDE.md right now? The repo file references a macOS path that other agents (in containers) can't read — is there a checked-in copy that's actually authoritative?
- Did the `.gitignore` slim in 3d2f085 actually fix Obsidian Sync conflict files, or just stop tracking them while leaving conflicts on disk?
- How many skills are on the agent-collab branch *now*? I think 6 but I know my view is pre-d950880.

## What other agents should know
- I'm on a different branch (`refactor/vault-paths`) — if you're diffing skills against main/agent-collab, my tree won't match and that's expected.
- Treat any claim I make about skill counts on agent-collab as stale — re-check before relying on it.
- The CLAUDE.md inheritance chain assumes a macOS filesystem layout; if you're a containerized agent and inheritance "looks broken", it probably is for you specifically.
- Lint is green on `refactor/vault-paths` as of ~08:38Z.

## Last action
2026-05-01T08:38Z — ran `npm run lint` (clean), then opened `vault/.obsidian/` to audit config files.
