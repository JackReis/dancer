import importlib.util
import io
import json
import sys
from pathlib import Path

HOOK = Path(__file__).resolve().parents[1] / "hooks" / "quad_memory_hook.py"


def _load():
    spec = importlib.util.spec_from_file_location("quad_memory_hook", HOOK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_user_prompt_submit_emits_brief_block(monkeypatch, capsys):
    from quad_memory.core import TurnMemory
    mod = _load()
    monkeypatch.setattr(
        mod.quad, "brief",
        lambda q, *, limit=5: [TurnMemory("holographic", "1", "verified handoff for quad", 0.5, "holographic")],
    )
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps({"prompt": "what did we decide about secrets?"})))
    rc = mod.main(["--event", "user-prompt-submit", "--source", "claude-code", "--limit", "5"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "quad-memory-brief" in out
    assert "verified handoff for quad" in out
    # stdout must be valid JSON carrying additionalContext
    payload = json.loads(out)
    assert "quad-memory-brief" in payload["hookSpecificOutput"]["additionalContext"]


def test_stop_calls_capture(monkeypatch):
    from quad_memory.core import PlaneResult
    mod = _load()
    called = {}

    def fake_capture(content, **kw):
        called["content"] = content
        called["kw"] = kw
        return [PlaneResult("holographic", True, "ok")]

    monkeypatch.setattr(mod.quad, "capture", fake_capture)
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps({"session_id": "s1", "cwd": "/tmp/proj", "prompt": "do the thing"})))
    rc = mod.main(["--event", "stop", "--source", "claude-code"])
    assert rc == 0
    assert "content" in called and called["content"]


def test_hook_is_fail_open(monkeypatch):
    mod = _load()

    def boom(*a, **k):
        raise RuntimeError("plane core down")

    monkeypatch.setattr(mod.quad, "brief", boom)
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps({"prompt": "x"})))
    rc = mod.main(["--event", "user-prompt-submit"])
    assert rc == 0  # never block a turn


def test_empty_stdin_is_safe(monkeypatch):
    mod = _load()
    monkeypatch.setattr(sys, "stdin", io.StringIO(""))
    assert mod.main(["--event", "stop"]) == 0
