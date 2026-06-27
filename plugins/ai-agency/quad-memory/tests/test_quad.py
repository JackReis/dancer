from quad_memory.core import TurnMemory, PlaneResult


def _tm(plane, content="x"):
    return TurnMemory(plane=plane, id=f"{plane}-1", content=content, score=0.5, source=plane)


def test_brief_aggregates_all_planes(monkeypatch):
    import quad_memory.quad as quad
    monkeypatch.setattr(quad.holographic, "search_holographic", lambda q, *, limit=5: [_tm("holographic")])
    monkeypatch.setattr(quad.hindsight, "recall_hindsight", lambda q, *, limit=5: [_tm("hindsight")])
    monkeypatch.setattr(quad.obn, "search_obn", lambda q, *, limit=5: [_tm("obn")])
    monkeypatch.setattr(quad.honcho_plane, "recall_honcho", lambda q, *, limit=1: [_tm("honcho")])
    mems = quad.brief("query", limit=10)
    assert {m.plane for m in mems} == {"holographic", "hindsight", "obn", "honcho"}


def test_brief_survives_one_plane_raising(monkeypatch):
    import quad_memory.quad as quad

    def boom(q, *, limit=5):
        raise RuntimeError("plane down")

    monkeypatch.setattr(quad.holographic, "search_holographic", boom)
    monkeypatch.setattr(quad.hindsight, "recall_hindsight", lambda q, *, limit=5: [_tm("hindsight")])
    monkeypatch.setattr(quad.obn, "search_obn", lambda q, *, limit=5: [])
    monkeypatch.setattr(quad.honcho_plane, "recall_honcho", lambda q, *, limit=1: [_tm("honcho")])
    mems = quad.brief("query", limit=10)
    planes = {m.plane for m in mems}
    assert "hindsight" in planes and "honcho" in planes
    assert "holographic" not in planes  # raised → dropped, fail-open


def test_capture_calls_every_plane(monkeypatch):
    import quad_memory.quad as quad
    calls = []

    def mk(plane):
        def _cap(content, **kwargs):
            calls.append(plane)
            return PlaneResult(plane, True, "ok")
        return _cap

    monkeypatch.setattr(quad.holographic, "capture_holographic", mk("holographic"))
    monkeypatch.setattr(quad.hindsight, "capture_hindsight", mk("hindsight"))
    monkeypatch.setattr(quad.obn, "capture_obn", mk("obn"))
    monkeypatch.setattr(quad.honcho_plane, "capture_honcho", mk("honcho"))

    results = quad.capture("verified handoff for quad", role="user", source="claude-code",
                           session_id="s1", kind="turn")
    assert all(isinstance(r, PlaneResult) for r in results)
    assert {r.plane for r in results} == {"holographic", "hindsight", "obn", "honcho"}
    assert set(calls) == {"holographic", "hindsight", "obn", "honcho"}


def test_capture_survives_one_plane_raising(monkeypatch):
    import quad_memory.quad as quad

    def boom(content, **kwargs):
        raise RuntimeError("capture down")

    monkeypatch.setattr(quad.holographic, "capture_holographic", boom)
    monkeypatch.setattr(quad.hindsight, "capture_hindsight", lambda c, **k: PlaneResult("hindsight", True, "ok"))
    monkeypatch.setattr(quad.obn, "capture_obn", lambda c, **k: PlaneResult("obn", True, "ok"))
    monkeypatch.setattr(quad.honcho_plane, "capture_honcho", lambda c, **k: PlaneResult("honcho", True, "ok"))

    results = quad.capture("verified handoff for quad", role="user", source="claude-code",
                           session_id="s1", kind="turn")
    by_plane = {r.plane: r for r in results}
    assert len(by_plane) == 4
    assert by_plane["holographic"].ok is False  # raised → fail-open PlaneResult
    assert by_plane["hindsight"].ok is True


def test_capture_rejects_secret(monkeypatch):
    import quad_memory.quad as quad
    import pytest
    with pytest.raises(ValueError):
        quad.capture("export AWS_SECRET_KEY=sk-abcdef1234567890abcdef", role="user",
                     source="claude-code", session_id="s1", kind="turn")


def test_status_returns_four_health_rows(monkeypatch):
    import quad_memory.quad as quad
    monkeypatch.setattr(quad.holographic, "holographic_health", lambda: PlaneResult("holographic", True, "ok"))
    monkeypatch.setattr(quad.hindsight, "hindsight_health", lambda: PlaneResult("hindsight", False, "down"))
    monkeypatch.setattr(quad.obn, "obn_health", lambda: PlaneResult("obn", True, "ok"))
    monkeypatch.setattr(quad.honcho_plane, "honcho_health", lambda: PlaneResult("honcho", True, "ok"))
    rows = quad.status()
    assert len(rows) == 4
    assert {r.plane for r in rows} == {"holographic", "hindsight", "obn", "honcho"}
