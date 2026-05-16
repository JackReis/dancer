# cross-check.md template
# Written by the merge writer after all rows are submitted.

# Cross-Check: <topic>

**Merge writer:** <agent-slug>
**Checked at:** <ISO8601 UTC>

## Summary

| Metric | Count |
|---|---|
| Total pairs (NxN) | <n² - n> |
| Aligned | <num> |
| Misaligned | <num> |
| Gaps | <num> |
| Unchecked | <num> |

## Pair Results

### ✅ Aligned: <agent-A> ↔ <agent-B>

- A expects X from B → B provides X ✓
- B expects Y from A → A provides Y ✓
- Workflow contract: <trigger> via <channel>, SLA <sla>

### ⚠️ Misaligned: <agent-A> ↔ <agent-C>

- A expects Slack notifications from C
- C provides email notifications only
- **Gap:** Communication channel mismatch

### ❓ Gap: <agent-A> ↔ <agent-D>

- A has `confidence: low` for this pair
- A notes: "Don't know D's deployment capabilities"
- **Recommendation:** A should query D before ratifying

## Suggested Actions

1. <Specific resolution for each misalignment>
2. ...