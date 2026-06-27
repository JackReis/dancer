# quad-memory

Per-turn **quad-plane memory** for Claude Code: **Hindsight + Holographic + Honcho + OBn**.
The Claude Code analogue of Hermes' triple-memory stack, extended to four planes.

## Planes

| Plane | Backend | Recall flavor |
|---|---|---|
| Holographic | SQLite FTS (`~/.hermes/memory_store.db`) | keyword/BM25 facts |
| Hindsight | HTTP daemon (`:9177`, bank `hermes`) | semantic recall |
| Honcho | Dialectic API (`:8000`, workspace `hermes`) | synthesized "what Honcho knows about Jack relevant to this prompt" |
| OBn | Chroma vault ingest (federated query) | vault semantic search |

Each plane is **fail-open**: an unreachable plane (or absent vault) degrades
gracefully and never blocks a turn.

## Architecture

- `quad_memory/` — vendored Python package, one module per plane plus `core.py`
  (dataclasses + secret scrubber) and `quad.py` (ThreadPoolExecutor fan-out).
- `hooks/` — per-turn hooks: `UserPromptSubmit` → brief (recall), `Stop` → capture (write).
- `commands/` — slash commands for manual brief / capture / status / ask (dialectic).
- `.mcp.json` — stdio MCP server exposing the manual tools.

## Provenance

The plane logic under `quad_memory/` is **vendored** from the live SSOT at
`=notes/scripts/fleet_memory/local_turn_sync.py` (+ `hindsight.py`) and the Honcho
reference client at `~/hermes-agent-jr/plugins/memory/honcho/`. Phase 2 will replace
the verbatim copies with a version-pinned vendor + drift check (self-contained first,
then hybrid).

## Status

Phase 1 — self-contained plugin (in progress).
