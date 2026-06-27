"""Quad orchestrator — fan out brief (recall) / capture (write) / status (health)
across all four planes concurrently, with per-plane fail-open.

`rerank_rrf` is copied verbatim from the live SSOT
    =notes/scripts/fleet_memory/local_turn_sync.py
The fan-out shape mirrors that file's `brief`/`capture`/`health`, extended from
three planes to four (Honcho added to both the brief and capture fan-outs).
Every plane call is wrapped so one plane raising never breaks the brief, the
capture batch, or the status table.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from quad_memory.core import TurnMemory, PlaneResult, reject_secret_content
from quad_memory import holographic, hindsight, obn, honcho_plane


def rerank_rrf(groups: list[list[TurnMemory]], *, limit: int) -> list[TurnMemory]:
    scored: dict[tuple[str, str], tuple[TurnMemory, float]] = {}
    for group in groups:
        for rank, memory in enumerate(group, 1):
            key = (memory.plane, memory.id)
            rrf = 1.0 / (60 + rank)
            previous = scored.get(key)
            total = memory.score + rrf + (previous[1] if previous else 0.0)
            scored[key] = (memory, total)
    ranked = sorted(scored.values(), key=lambda item: item[1], reverse=True)
    return [
        TurnMemory(
            plane=memory.plane,
            id=memory.id,
            content=memory.content,
            score=score,
            source=memory.source,
            metadata={**memory.metadata, "reranker": "reciprocal_rank_fusion"},
        )
        for memory, score in ranked[:limit]
    ]


def _safe_group(fn) -> list[TurnMemory]:
    """Run a recall callable; on any failure return an empty group (fail-open)."""
    try:
        return fn() or []
    except Exception:
        return []


def _safe_result(plane: str, fn) -> PlaneResult:
    """Run a capture/health callable; on any failure return a fail-open PlaneResult."""
    try:
        return fn()
    except Exception as exc:
        return PlaneResult(plane, False, f"{plane} raised: {exc}")


def brief(query: str, *, limit: int = 5) -> list[TurnMemory]:
    """Concurrent recall across all four planes → merged + RRF-ranked memories."""
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(_safe_group, lambda: holographic.search_holographic(query, limit=limit)),
            executor.submit(_safe_group, lambda: hindsight.recall_hindsight(query, limit=limit)),
            executor.submit(_safe_group, lambda: obn.search_obn(query, limit=limit)),
            executor.submit(_safe_group, lambda: honcho_plane.recall_honcho(query, limit=max(1, limit))),
        ]
        groups = [future.result() for future in futures]
    return rerank_rrf(groups, limit=limit)


def capture(content: str, *, role: str, source: str, session_id: str, kind: str = "turn",
            task_id: str | None = None) -> list[PlaneResult]:
    """Concurrent write across all four planes → list[PlaneResult].

    Rejects secret-looking content up front (raises ValueError) so no secret is
    ever written to any plane.
    """
    reject_secret_content(content)
    task_id = task_id or f"session/{session_id}"
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(_safe_result, "holographic",
                            lambda: holographic.capture_holographic(content, source=source, session_id=session_id, task_id=task_id, kind=kind)),
            executor.submit(_safe_result, "hindsight",
                            lambda: hindsight.capture_hindsight(content, source=source, session_id=session_id, task_id=task_id, kind=kind)),
            executor.submit(_safe_result, "obn",
                            lambda: obn.capture_obn(content, source=source, session_id=session_id, kind=kind)),
            executor.submit(_safe_result, "honcho",
                            lambda: honcho_plane.capture_honcho(content, role=role, source=source, session_id=session_id)),
        ]
        return [future.result() for future in futures]


def status() -> list[PlaneResult]:
    """Concurrent health probe across all four planes → 4 health rows."""
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(_safe_result, "holographic", holographic.holographic_health),
            executor.submit(_safe_result, "hindsight", hindsight.hindsight_health),
            executor.submit(_safe_result, "obn", obn.obn_health),
            executor.submit(_safe_result, "honcho", honcho_plane.honcho_health),
        ]
        return [future.result() for future in futures]
