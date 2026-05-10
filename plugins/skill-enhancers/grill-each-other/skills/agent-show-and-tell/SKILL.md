---
name: agent-show-and-tell
description: Each agent in a local fleet — Claude sessions on different machines, mixed-model agents, or whatever's in play — independently writes a short "what I know and what I'm working on" report to a shared directory. One reader collates them into a roundup. No grilling, no consensus, no merging. Use when you want visibility across a multi-agent fleet, or the user mentions "fleet show and tell", "agent roundup", "what does each agent know", or "round-robin status from the agents".
---

Show-and-tell is the **simplest** multi-agent coordination skill in this repo. Each agent writes one file describing what it knows. One reader (an agent or the user) collates. That's the whole protocol. No conflict resolution, no convergence — if reports disagree, the conflict gets *named* in the roundup but not resolved.

This is the right starting point. If you find yourself wanting consensus on disputed claims, graduate to `peer-grill`. If you want one agent to teach another, use `teach-an-agent`.

## Working directory

`.show-and-tell/<topic>/` relative to repo root, where `<topic>` is a short slug (e.g. `monday-status`, `infra-state`, `release-readiness`). Default to today's ISO date if unspecified.

| File | Writers | Purpose |
|---|---|---|
| `<agent>.md` | only that agent | the agent's report (with facet frontmatter) |
| `roundup.md` | one designated reader (any agent, or the user) | collated view across all reports |
| `roundup.<facet>=<value>.md` | optional, any reader | filtered roundup ("lens") for one facet — e.g. `roundup.project=dev-workspace.md` |
| `_meta.yaml` | first agent to start the topic | participants, topic description, start time |

## Facets — multilayer grouping

Each agent's identity carries a flat set of facets so the fleet can be sliced by any dimension. Standard facets (use these names verbatim where they apply):

| Facet | Meaning | Examples |
|---|---|---|
| `project` | the codebase / repo / product the session is acting on | `dev-workspace`, `infra-terraform`, `web-app` |
| `harness` | the runtime executing the agent | `claude-code-cli`, `claude-code-web`, `claude-desktop`, `cursor`, `openhands`, `custom-sdk` |
| `provider` | the model API behind the agent | `anthropic`, `openai`, `google`, `local-ollama`, `bedrock` |
| `surface` | where the human interacts | `terminal`, `web`, `vscode`, `slack-bot`, `cli-pipe` |
| `machine` | hostname or stable machine id | `mac-jr`, `linux-vm-1`, `ci-runner` |
| `user` | who's at the keyboard | `jack`, `automation`, `ci` |

Add other facets freely (e.g. `environment: prod`, `branch: feature-x`, `team: platform`) — they just need to be consistent across reports if you want to roll up by them later. When in doubt, prefer flat facets over nested namespaces.

## Setup — ask the user before any writes

1. **Topic** — what's the show-and-tell about? Get a slug.
2. **Identity** — what name is *this* agent? (`claude-laptop`, `claude-pr-bot`, `cursor-mac`, etc.)
3. **Participants** — who else is in the fleet for this topic? Used by the roundup reader to know when everyone's reported in. If you don't know, list yourself and note "tbd — others may join."
4. **Reader** — who's writing the roundup? (default: whichever agent finishes last; alternative: the user.)

If `_meta.yaml` doesn't exist yet, create it with the participants list and topic description. If it does, read it and confirm your identity is in the list — append yourself if not.

## Report — write `<agent>.md`

Use this exact template. It's optimized for fast reading by both humans and other agents. Don't add sections. Don't omit sections — write "(none)" if a section doesn't apply. The YAML frontmatter is mandatory and must come first.

```markdown
---
agent: <agent-name>
topic: <topic-slug>
session_started: <ISO8601 — when the *agent's session* started, NOT the report-write time>
facets:
  project: <slug>
  harness: <slug>
  provider: <slug>
  surface: <slug>
  machine: <hostname-or-id>
  user: <username>
  # extra facets (e.g. branch:, environment:, team:) go in this same block.
  # omit any standard facet that doesn't apply. drop this comment line in the actual report.
---

# <agent-name> — <topic>

## What I'm working on
<one paragraph — the active task, not the project at large>

## What I know
<bulleted facts I currently hold to be true. Each bullet:>
- **<short claim>** — source: <file:line, command output, prior decision, or "inferred">; confidence: high | medium | low

## Open questions
<things I'm uncertain about that another agent might have already resolved>
- ...

## What other agents should know
<the 1–5 most useful things to surface — don't repeat "What I know" verbatim>
- ...

## Last action
<one line: the most recent concrete thing I did, with timestamp>
```

Rules:
- **Don't read other agents' reports before writing your own.** Blind reports prevent groupthink and let the reader detect *real* consensus rather than echoing.
- Confidence levels mean the same thing as in `peer-grill`: `high` requires a *checkable source you can cite* (file:line, command output, signed-off doc) — session-memory inference does not qualify; `medium` is inferred from possibly-stale signal; `low` is guess.
- Sources can be plural — list multiple if a claim is supported by more than one. Use `inferred` (no external source) sparingly and only with `medium` or `low` confidence.
- For "Last action," include an absolute ISO8601 timestamp; relative time ("4 minutes ago") is OK as a parenthetical but not as the primary format.
- Every body section is mandatory. If a section truly has no content, write `(none)` *under* the heading — don't skip the heading itself.
- Keep it short. A report longer than ~60 lines is too long; split the topic.

## Roundup — write `roundup.md`

The designated reader (or whichever agent is last to report) reads every `<agent>.md` and writes a single roundup with this structure:

```markdown
# <topic> — roundup

**Generated by:** <reader-name> at <ISO8601>
**Participants reported:** <list of agents who submitted>
**Missing:** <participants from _meta.yaml who didn't report>

## Fleet shape

| Facet | Values present |
|---|---|
| project | <values from frontmatter, with counts> |
| harness | ... |
| provider | ... |
| (etc.) | ... |

## Consensus
<facts that appeared in 2+ reports without contradiction. Cite each agent and its source:>
- **<claim>** — agent-A (`<source>`), agent-B (`<source>`)

## Solo facts
<facts only one agent reported. Group by agent:>
### From <agent-A>
- ...

## Conflicts
<facts where two reports disagree. Name them; don't resolve them.>
- **<topic>** — agent-A says X (source: ...); agent-B says Y (source: ...) → suggest peer-grill if this matters

## Cross-facet observations
<things visible only when you slice the reports by facets. E.g. "all three cursor-harness agents reported the same MCP timeout — likely harness-specific". Cite which agents support each observation.>
- ...

## Open questions across the fleet
<merged from each agent's "Open questions" section, with which agent asked:>
- ...

## Suggested next actions
<short, specific. Cite the report(s) that motivate each suggestion.>
- ...
```

## Lenses — `roundup.<facet>=<value>.md` (optional)

When a fleet spans multiple projects, harnesses, or providers, a single roundup can be too noisy. A *lens* is a filtered roundup where you only collate reports matching one facet value. File naming: `roundup.<facet>=<value>.md` (e.g. `roundup.project=dev-workspace.md`, `roundup.harness=cursor.md`).

Lens contents follow the same template as the master roundup, but the participant list is restricted to agents matching the filter, and "Cross-facet observations" is replaced with "Within-<facet> observations." Generate lenses on demand — don't pre-generate one for every facet value.

Rules:
- **Do not invent claims** in the roundup. Every line traces to a `<agent>.md`.
- **Do not resolve conflicts.** Name them and move on. Resolving conflicts is `peer-grill`'s job.
- If a participant in `_meta.yaml` didn't submit a report, list them as missing — don't proceed as if they had nothing to add.

## Guardrails

- This skill is **fire-and-forget**. Each agent writes once and is done. No loop, no rounds.
- If you (the agent running this skill) are the reader, write the roundup *after* a quick sanity pause — re-read each report once before collating. Roundups written too fast tend to drop the conflicts.
- If two agents have the same identity (someone forgot to differentiate), the second one to write clobbers the first. Detect the collision (file already exists with the same name) and refuse to overwrite — ask the user to disambiguate first.
- Commit `.show-and-tell/<topic>/` to git when done so the snapshot is auditable.
