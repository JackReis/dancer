# Quick Workflow

Fast single-round perspective check. Use for sanity checks and quick feedback.

## Purpose

Single-round council check — compose 4 topic-specific custom agents, get their immediate takes in parallel. When the quick check reveals disagreement or complexity, recommend escalating to the full DEBATE workflow.

## Prerequisites

- Topic or question to evaluate
- Optional: Custom council members

## Execution

### Step 1: Compose & Announce Quick Council

Compose 4 agents with topic-specific traits via Agent dispatch, then announce:

```markdown
## Quick Council: [Topic]

**Council Members:** [List composed agent names]
**Mode:** Single round (fast perspectives)
```

### Step 2: Parallel Perspective Gathering

Launch all council members in parallel using `subagent_type: "general-purpose"`.

Each agent prompt includes the composed agent's full prompt PLUS:
```
QUICK COUNCIL CHECK

Topic: [The topic]

[Relevant context for the topic]

Give your immediate take from your specialized perspective:
- Key concern, insight, or recommendation
- 30-50 words max
- Be direct and specific
```

### Step 3: Output Perspectives

```markdown
### Perspectives

**[Agent 1 Name] ([traits]):**
[Brief take]

**[Agent 2 Name] ([traits]):**
[Brief take]

**[Agent 3 Name] ([traits]):**
[Brief take]

**[Agent 4 Name] ([traits]):**
[Brief take]

### Quick Summary

**Consensus:** [Do they generally agree? On what?]
**Concerns:** [Any red flags raised?]
**Recommendation:** [Proceed / Reconsider / Need full debate]
```

## When to Escalate

If the quick check reveals significant disagreement or complex trade-offs:

```
This topic has enough complexity for a full council debate.
Run: "Council: [topic]" for 3-round structured discussion.
```

## Timing

| Phase | Duration | Parallelism |
|-------|----------|-------------|
| Composition | 5-10 sec | Agent dispatch calls |
| Round 1 | 10-20 sec | All agents parallel |
| Synthesis | 5 sec | Sequential |

**Total: 15-30 seconds for quick check**
