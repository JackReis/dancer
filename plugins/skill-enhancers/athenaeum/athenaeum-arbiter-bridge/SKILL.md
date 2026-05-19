---
name: athenaeum-arbiter-bridge
description: Bridge athenaeum-audit divergence findings to Arbiter Zebu for human-in-the-loop decisions. Use when audit finds High Risk or Divergent risks that require human approval before ratification.
version: 0.1.0
---

# Athenaeum-Arbiter Bridge

Escalates athenaeum-audit findings that require human judgment to Arbiter Zebu.

## When to Use

- After `athenaeum-audit` produces a triangulation report with "Divergent" or "High Risk" risks
- Before `fleet-ratify` on items flagged as high-risk during audit
- When a plan has architectural tradeoffs that need human sign-off

## DO NOT Use For

- Simple yes/no questions (use direct message instead)
- Low-risk findings (athenaeum-reconcile can handle those)
- Urgent real-time decisions (this is async)

## Tools

### arbiter_push

Create a decision plan from audit findings.

**CLI:** `arbiter-push '<json>'`

Takes a single JSON argument:
```json
{
  "title": "Governance: Divergent Claims in Agent Stack",
  "tag": "athenaeum-audit",
  "priority": "high",
  "context": "athenaeum-audit found divergent claims between agents...",
  "notify": "agent:opencode:main",
  "decisions": [
    {
      "id": "claim-resolution",
      "title": "How to resolve divergent claim X?",
      "context": "Agent A says X, Agent B says Y",
      "options": [
        {"key": "a", "label": "Accept Agent A's claim", "note": "Rationale for A"},
        {"key": "b", "label": "Accept Agent B's claim", "note": "Rationale for B"},
        {"key": "merge", "label": "Merge both", "note": "Synthesize both claims"}
      ],
      "allowCustom": true
    }
  ]
}
```

Returns: `{"planId": "abc123", "file": "~/.arbiter/queue/pending/...", "status": "pending"}`

### arbiter_check

Check if a decision has been answered.

**CLI:** `arbiter-status <plan-id>` or `arbiter-status --tag <tag>`

Returns: `{"planId": "abc123", "status": "completed", "answers": {...}}`

## Integration with Governance Loop

1. **Audit** (athenaeum-audit) produces triangulation report
2. **Escalate** (this skill) pushes divergent/high-risk findings to Arbiter Zebu
3. **Human decides** via Telegram buttons (zero LLM cost)
4. **Verify** (fleet-ratify) checks for `arbiter_decision_id` on high-risk items
5. **Ratify** commits with both Durable Evidence and Human Approval

## File Locations

| Path | Purpose |
|------|---------|
| `~/.arbiter/queue/pending/` | Plans awaiting human review |
| `~/.arbiter/queue/completed/` | Answered plans (archive) |
| `~/.arbiter/queue/notify/` | Agent notifications |