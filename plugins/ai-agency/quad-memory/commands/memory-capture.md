---
description: Capture one durable fact across all four memory planes (secret-scrubbed)
argument-hint: <text to remember>
allowed-tools: mcp__quad-memory__memory_capture
---

Call `mcp__quad-memory__memory_capture` with `content` set to "$ARGUMENTS"
(`role` "assistant", `kind` "turn"). Report which planes accepted the write
using the returned per-plane results. If the capture was refused because the
content looks like a secret (`ok: false` with an error), tell the user and do
NOT retry or rephrase to bypass the scrubber.
