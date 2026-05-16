# Athenaeum

A dialectic skill pack for agent design, multi-agent reconciliation, and fleet-wide attestation.

> *"An unexamined claim does not exist."*

## Install

```bash
npx skills add jack-reis/dancer@athenaeum-design
npx skills add jack-reis/dancer@athenaeum-reconcile
npx skills add jack-reis/dancer@athenaeum-ratify
```

Or clone and symlink into your agent's `skills/` directory.

## Three skills, one lineage

| Skill | Purpose | When to use |
|---|---|---|
| `athenaeum-design` | Rigorous design grilling | Designing agents, architectures, plans |
| `athenaeum-reconcile` | Multi-agent state reconciliation | Two+ agents disagree; triangulate across models |
| `athenaeum-ratify` | Fleet attestation with dissent recording | N agents must sign off on an immutable artifact |

## Quick decision tree

```
Who is debating?
├── Just you + one agent → athenaeum-design
├── Two+ agents disagree → athenaeum-reconcile
│   └── Low stakes? → quick mode (no crypto)
│   └── High stakes? → formal mode (SHA-256 sign-offs)
└── Whole fleet must approve → athenaeum-ratify
    └── Unanimous? → ratified
    └── Dissent? → decomposed to human grain-gate
```

## Bootstrap

Each skill includes a unified CLI:

```bash
# Add scripts/ to PATH, then:
athenaeum init my-topic --mode design
athenaeum init my-topic --mode reconcile
athenaeum init my-topic --mode ratify --roster claude-laptop,kimi-cloud,neo

athenaeum diff my-topic
athenaeum sign my-topic
athenaeum check          # find ratifications awaiting your vote
```

## Philosophy

- **Progressive disclosure** — SKILL.md is the quick-start (<100 lines). REFERENCE.md is the deep protocol. Agents load the quick-start; read the deep docs only when executing.
- **Mode selection** — Not every reconciliation needs cryptographic proof. `quick` mode handles the common case; `formal` mode handles cross-machine, cross-model stakes.
- **Code-anchored** — Claims cite file paths and line ranges. The repo wins; agent recollection does not.
- **Cross-agent** — Works in Claude Code, Kimi, Codex, Gemini, OpenHands, or human-driven sessions. Auto-detects runtime or falls back to env vars.

## Structure

```
athenaeum/
├── athenaeum-design/SKILL.md
├── athenaeum-reconcile/SKILL.md
├── athenaeum-ratify/SKILL.md
├── REFERENCE.md           # Deep protocol for all three
├── scripts/
│   └── athenaeum          # Unified bootstrap CLI
└── templates/
    ├── design/
    ├── reconcile/
    └── ratify/
```

## Roadmap / open questions

- [ ] Package for `npx skills add`
- [ ] Add `athenaeum-audit` (code-aware agent-stack audit + reconcile in one pass)
- [ ] Star-topology multi-peer reconciliation (currently pairwise chains only)
- [ ] Auto-discovery of fleet roster from `~/Documents/Coordination/` or env var
