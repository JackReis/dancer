import json

from quad_memory.core import TurnMemory, PlaneResult


def test_memory_status_returns_serializable_dict(monkeypatch):
    import quad_memory.mcp_server as mcp
    monkeypatch.setattr(mcp.quad, "status",
                        lambda: [PlaneResult("holographic", True, "ok"), PlaneResult("honcho", False, "down")])
    out = mcp.tool_memory_status()
    json.dumps(out)  # must be serializable
    assert out["ok"] is True and len(out["planes"]) == 2


def test_memory_brief_returns_serializable_dict(monkeypatch):
    import quad_memory.mcp_server as mcp
    monkeypatch.setattr(mcp.quad, "brief",
                        lambda q, *, limit=5: [TurnMemory("holographic", "1", "verified handoff", 0.5, "holographic")])
    out = mcp.tool_memory_brief("query", limit=3)
    json.dumps(out)
    assert out["query"] == "query" and out["results"][0]["plane"] == "holographic"


def test_memory_capture_returns_serializable_dict(monkeypatch):
    import quad_memory.mcp_server as mcp
    monkeypatch.setattr(mcp.quad, "capture", lambda content, **k: [PlaneResult("obn", True, "ok")])
    out = mcp.tool_memory_capture("verified handoff", role="user", kind="turn")
    json.dumps(out)
    assert out["ok"] is True


def test_memory_capture_catches_secret_error(monkeypatch):
    import quad_memory.mcp_server as mcp

    def boom(content, **k):
        raise ValueError("refusing to capture content that looks like a secret")

    monkeypatch.setattr(mcp.quad, "capture", boom)
    out = mcp.tool_memory_capture("export OPENAI_API_KEY=sk-abcdef1234567890abcdef", role="user")
    json.dumps(out)
    assert out["ok"] is False and "error" in out


def test_memory_ask_dialectic_passthrough(monkeypatch):
    import quad_memory.mcp_server as mcp
    monkeypatch.setattr(mcp.honcho_plane, "recall_honcho",
                        lambda q, *, limit=1: [TurnMemory("honcho", "honcho-dialectic-1", "Jack prefers SOPS", 1.0, "honcho-dialectic")])
    out = mcp.tool_memory_ask("what about secrets?")
    json.dumps(out)
    assert "SOPS" in out["answer"]


def test_memory_search_plane(monkeypatch):
    import quad_memory.mcp_server as mcp
    monkeypatch.setattr(mcp.obn, "search_obn",
                        lambda q, *, limit=5: [TurnMemory("obn", "core:path.md", "c", 0.5, "obn")])
    out = mcp.tool_memory_search_plane("obn", "query", limit=2)
    json.dumps(out)
    assert out["plane"] == "obn" and len(out["results"]) == 1
    bad = mcp.tool_memory_search_plane("nope", "query")
    assert bad["ok"] is False and "error" in bad
