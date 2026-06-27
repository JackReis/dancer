---
description: Ask Honcho's Dialectic API what it knows about Jack relevant to your question
argument-hint: <question>
allowed-tools: mcp__quad-memory__memory_ask
---

Call `mcp__quad-memory__memory_ask` with `query` set to "$ARGUMENTS". Present
the synthesized `answer` field, noting that it is Honcho's dialectic synthesis
of what it knows about Jack relevant to the question — not a raw vector hit. If
`answer` is empty, say Honcho had no relevant synthesis (the deriver may still
be catching up on recent writes).
