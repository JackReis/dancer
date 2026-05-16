# ratified-matrix.md template
# Written by the merge writer on full ratification.
# This is the terminal artifact — the confirmed fleet topology.

# Ratified Fleet Topology: <topic>

**Ratified at:** <ISO8601 UTC>
**SHA-256:** <sha256-hash of ratified-matrix.json>
**Roster:** <agent-a>, <agent-b>, <agent-c>

## Topology Map

| From ↓ / To → | <agent-a> | <agent-b> | <agent-c> |
|---|---|---|---|
| **<agent-a>** | — | provides/expects | provides/expects |
| **<agent-b>** | provides/expects | — | provides/expects |
| **<agent-c>** | provides/expects | provides/expects | — |

## Relationship Details

### <agent-a> → <agent-b>

**A provides to B:**
- <item 1>
- <item 2>

**A expects from B:**
- <item 1>
- <item 2>

**Workflow contract:**
- Trigger: <trigger>
- Channel: <channel>
- Format: <format>
- SLA: <sla>

### <agent-b> → <agent-a>

(Reciprocal relationship — may differ from the above)

## Signatures

| Agent | Signed at | SHA-256 verified |
|---|---|---|
| <agent-a> | <ISO8601> | ✓ |
| <agent-b> | <ISO8601> | ✓ |
| <agent-c> | <ISO8601> | ✓ |