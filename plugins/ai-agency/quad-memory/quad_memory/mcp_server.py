#!/usr/bin/env python3
"""Quad-memory MCP server — manual tool surface over the four planes.

Mirrors ~/ai-dev/claude-main/claude/agents/fleet-memory/fleet_memory_mcp_server.py.
The MCP SDK is imported lazily (inside build_server / main) so the tool handler
functions below import cleanly without the SDK or a live container — this keeps
the handlers unit-testable and the plugin importable on hosts without `mcp`.

Tools:
  memory_status                         → quad.status()
  memory_brief(query, limit)            → quad.brief()
  memory_capture(content, role, kind)   → quad.capture()
  memory_ask(query)                     → recall_honcho()  (explicit dialectic)
  memory_search_plane(plane, query, n)  → single-plane search
"""

from __future__ import annotations

import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

# Make `quad_memory` importable when launched as a standalone script (the way
# .mcp.json runs it: `python3 .../quad_memory/mcp_server.py`). That puts the
# `quad_memory/` dir on sys.path[0], NOT the plugin root (its package parent),
# so the package import below fails without this shim. Mirrors hooks/quad_memory_hook.py.
PLUGIN_ROOT = Path(__file__).resolve().parents[1]
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from quad_memory import quad, holographic, hindsight, obn, honcho_plane  # noqa: E402


# --- Tool handlers (pure, serializable-dict returns; unit-tested directly) ----

def tool_memory_status() -> dict[str, Any]:
    rows = quad.status()
    return {"ok": any(r.ok for r in rows), "planes": [asdict(r) for r in rows]}


def tool_memory_brief(query: str, limit: int = 5) -> dict[str, Any]:
    mems = quad.brief(query, limit=limit)
    return {"ok": bool(mems), "query": query, "results": [asdict(m) for m in mems]}


def tool_memory_capture(content: str, role: str = "assistant", kind: str = "turn",
                        source: str = "claude-code", session_id: str | None = None) -> dict[str, Any]:
    session_id = session_id or "mcp-manual"
    try:
        results = quad.capture(content, role=role, source=source, session_id=session_id, kind=kind)
    except ValueError as exc:  # secret scrubber refused the content
        return {"ok": False, "error": str(exc)}
    return {"ok": any(r.ok for r in results), "planes": [asdict(r) for r in results]}


def tool_memory_ask(query: str) -> dict[str, Any]:
    mems = honcho_plane.recall_honcho(query, limit=1)
    return {
        "ok": bool(mems),
        "query": query,
        "answer": mems[0].content if mems else "",
        "results": [asdict(m) for m in mems],
    }


def tool_memory_search_plane(plane: str, query: str, limit: int = 5) -> dict[str, Any]:
    searchers = {
        "holographic": lambda: holographic.search_holographic(query, limit=limit),
        "hindsight": lambda: hindsight.recall_hindsight(query, limit=limit),
        "obn": lambda: obn.search_obn(query, limit=limit),
        "honcho": lambda: honcho_plane.recall_honcho(query, limit=max(1, limit)),
    }
    searcher = searchers.get(plane)
    if searcher is None:
        return {"ok": False, "error": f"unknown plane: {plane}", "results": []}
    mems = searcher()
    return {"ok": bool(mems), "plane": plane, "query": query, "results": [asdict(m) for m in mems]}


# --- MCP transport (lazy SDK import) -----------------------------------------

def build_server():
    import json
    from mcp.server import Server
    from mcp.types import TextContent, Tool

    server = Server("quad-memory")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(name="memory_status",
                 description="Health of all four memory planes (Holographic, Hindsight, Honcho, OBn).",
                 inputSchema={"type": "object", "properties": {}, "required": []}),
            Tool(name="memory_brief",
                 description="Recall across all four planes (RRF-ranked) for a query.",
                 inputSchema={"type": "object", "properties": {
                     "query": {"type": "string"},
                     "limit": {"type": "integer", "default": 5, "minimum": 1, "maximum": 20},
                 }, "required": ["query"]}),
            Tool(name="memory_capture",
                 description="Capture one durable fact across all four planes (secret-scrubbed).",
                 inputSchema={"type": "object", "properties": {
                     "content": {"type": "string"},
                     "role": {"type": "string", "default": "assistant", "enum": ["user", "assistant"]},
                     "kind": {"type": "string", "default": "turn"},
                 }, "required": ["content"]}),
            Tool(name="memory_ask",
                 description="Ask Honcho's Dialectic API what it knows about Jack relevant to a question.",
                 inputSchema={"type": "object", "properties": {
                     "query": {"type": "string"},
                 }, "required": ["query"]}),
            Tool(name="memory_search_plane",
                 description="Search a single plane (holographic | hindsight | obn | honcho).",
                 inputSchema={"type": "object", "properties": {
                     "plane": {"type": "string", "enum": ["holographic", "hindsight", "obn", "honcho"]},
                     "query": {"type": "string"},
                     "limit": {"type": "integer", "default": 5, "minimum": 1, "maximum": 20},
                 }, "required": ["plane", "query"]}),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: Any) -> list[TextContent]:
        arguments = arguments or {}
        if name == "memory_status":
            payload = tool_memory_status()
        elif name == "memory_brief":
            payload = tool_memory_brief(arguments["query"], int(arguments.get("limit", 5)))
        elif name == "memory_capture":
            payload = tool_memory_capture(arguments["content"], arguments.get("role", "assistant"),
                                          arguments.get("kind", "turn"))
        elif name == "memory_ask":
            payload = tool_memory_ask(arguments["query"])
        elif name == "memory_search_plane":
            payload = tool_memory_search_plane(arguments["plane"], arguments["query"],
                                               int(arguments.get("limit", 5)))
        else:
            payload = {"ok": False, "error": f"Unknown tool: {name}"}
        return [TextContent(type="text", text=json.dumps(payload, indent=2))]

    return server


async def _run() -> None:
    from mcp.server.stdio import stdio_server
    server = build_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main() -> None:
    # --selftest: prove the standalone launch reaches its imports (the way
    # .mcp.json runs the script). Exits 0 without starting the stdio transport.
    if "--selftest" in sys.argv:
        print("quad-memory mcp ok")
        return
    import asyncio
    asyncio.run(_run())


if __name__ == "__main__":
    main()
