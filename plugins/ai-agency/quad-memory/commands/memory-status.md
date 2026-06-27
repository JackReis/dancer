---
description: Show health of all four quad-memory planes (Holographic, Hindsight, Honcho, OBn)
allowed-tools: mcp__quad-memory__memory_status
---

Call the `mcp__quad-memory__memory_status` tool. Present the four plane health
rows as a compact table with columns: plane, ok, detail, count. Flag any plane
reporting `ok: false` so the user knows which backend is unreachable.
