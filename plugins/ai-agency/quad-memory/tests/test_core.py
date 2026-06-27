from quad_memory.core import reject_secret_content, stable_memory_id, TurnMemory, PlaneResult
import pytest


def test_secret_content_rejected():
    with pytest.raises(ValueError):
        reject_secret_content("export OPENAI_API_KEY=sk-abcdef1234567890abcdef")


def test_clean_content_passes():
    reject_secret_content("blocked on commit; verified handoff")  # no raise


def test_stable_memory_id_is_deterministic():
    a = stable_memory_id("claude-code", "sess1", "hello")
    b = stable_memory_id("claude-code", "sess1", "hello")
    assert a == b and a.startswith("claude-code_sess1_")


def test_dataclasses_constructible():
    tm = TurnMemory(plane="holographic", id="1", content="x", score=0.5, source="src")
    assert tm.plane == "holographic" and tm.metadata == {}
    pr = PlaneResult("honcho", True, "ok")
    assert pr.ok and pr.id is None and pr.count is None
