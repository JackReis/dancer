# Agent Design — `<NAME>`

> Output of `/grill-me-agents` or `/grill-me-with-agents`. Replace every `<...>` placeholder. Delete sections that genuinely don't apply (and explain why).

**Status:** draft | accepted | superseded
**Last grilled:** `<YYYY-MM-DD>`
**Supersedes:** `<path/to/previous/AGENT_DESIGN.md or "—">`

---

## 1. Goal & success criteria

- **Outcome produced:** `<one sentence>`
- **Done when:** `<concrete, observable signal — not "looks good">`
- **Explicitly out of scope:** `<...>`

## 2. Roster

| Agent | Single responsibility | Why not folded into another agent |
|---|---|---|
| `<name>` | `<...>` | `<...>` |

## 3. Topology

- **Pattern:** orchestrator-with-workers | pipeline | peer-to-peer | supervisor-tree | state-machine
- **Concurrency:** sequential | parallel-fanout | mixed (specify)

```
<ASCII diagram — boxes for agents, arrows for handoffs, label each arrow>
```

## 4. Context boundaries (read visibility)

| Agent | Sees | Hidden from it | Why hidden |
|---|---|---|---|
| `<name>` | `<...>` | `<...>` | `<...>` |

## 5. Handoff contracts

For each edge in the topology:

### `<sender> → <receiver>`
- **Schema:** `<type signature, JSON shape, or link>`
- **Validator:** `<who checks it, where>`
- **On schema drift:** `<retry | escalate | fail closed>`

## 6. Shared state (mutable, persisted)

- **Store:** `<file path | DB | MCP resource | env>`
- **Schema:** `<...>`
- **Writers:** `<which agents>`
- **Conflict resolution:** `<last-write-wins | CRDT | supervisor arbitrates | ...>`
- **TTL / cleanup:** `<...>`

## 7. Tool access (blast radius)

| Agent | Tools | Blast radius (what's the worst it can do?) |
|---|---|---|
| `<name>` | `<list>` | `<...>` |

## 8. Per-agent failure modes

| Agent | Failure | Detection | Recovery |
|---|---|---|---|
| `<name>` | loop / refusal / timeout / partial | `<...>` | `<...>` |

## 9. Inter-agent disagreement & authority

- **Precedence rules:** `<who overrides whom, on what grounds>`
- **Tie-break:** `<HITL | supervisor | abort>`

## 10. Human-in-the-loop

- **Triggers:** `<low confidence | destructive op | budget exceeded | ...>`
- **Minimum context shown to user:** `<...>`
- **Default action if user is absent:** `<...>`

## 11. Termination

- **Stop conditions:** `<explicit signal | budget | consensus | HITL veto | supervisor decision>`
- **On stop:** `<persist state? emit summary? notify?>`

## 12. Observability

- **Logged:** `<per-turn inputs, outputs, tool calls, costs>`
- **Trace location:** `<...>`
- **Replayable:** yes | partial | no — `<why>`

## 13. Cost & latency budget

| Agent | Model | Token budget / turn | Expected wall-clock |
|---|---|---|---|
| `<name>` | `<opus-4-7 | sonnet-4-6 | haiku-4-5>` | `<...>` | `<...>` |

- **Under pressure, cut first:** `<which agent or branch>`

## Open risks

- `<unresolved branch or known weakness>`

## Diff vs previous design (if any)

- **Added:** `<...>`
- **Removed:** `<...>`
- **Changed:** `<...>`
