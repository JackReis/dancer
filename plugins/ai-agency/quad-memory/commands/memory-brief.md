---
description: Recall across all four memory planes (RRF-ranked) for a query
argument-hint: <query>
allowed-tools: mcp__quad-memory__memory_brief
---

Call `mcp__quad-memory__memory_brief` with `query` set to "$ARGUMENTS" and
`limit` 5. Summarize the ranked results, grouping by plane and citing each
result's plane and id. If no results come back, say the planes returned nothing
for this query rather than inventing context.
