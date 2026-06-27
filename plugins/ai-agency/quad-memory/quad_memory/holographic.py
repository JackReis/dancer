"""Holographic plane — SQLite FTS5 facts store.

VENDORED COPY — `fts_query`, `holographic_health`, `capture_holographic`,
`search_holographic` are copied verbatim from the live SSOT
    =notes/scripts/fleet_memory/local_turn_sync.py
with one adaptation: the module-level `HOLOGRAPHIC_DB` default is now
env-overridable (`HOLOGRAPHIC_DB`) so the vendored plugin is path-portable.
Phase 2 will replace this verbatim copy with a version-pinned vendor + drift
check.
"""

from __future__ import annotations

import os
import re
import sqlite3
from pathlib import Path

from quad_memory.core import TurnMemory, PlaneResult, stable_memory_id


HOLOGRAPHIC_DB = Path(os.environ.get("HOLOGRAPHIC_DB", Path.home() / ".hermes" / "memory_store.db"))


def fts_query(query: str) -> str:
    terms = re.findall(r"[A-Za-z0-9_]{3,}", query.lower())
    terms = list(dict.fromkeys(terms))[:12]
    if not terms:
        return ""
    return " OR ".join(f'"{term}"' for term in terms)


def holographic_health(db_path: Path = HOLOGRAPHIC_DB) -> PlaneResult:
    if not db_path.exists():
        return PlaneResult("holographic", False, f"missing db: {db_path}")
    try:
        with sqlite3.connect(str(db_path)) as con:
            active = con.execute("SELECT COUNT(*) FROM facts WHERE deleted_at IS NULL").fetchone()[0]
        return PlaneResult("holographic", True, "sqlite facts table reachable", count=int(active))
    except sqlite3.Error as exc:
        return PlaneResult("holographic", False, f"sqlite error: {exc}")


def capture_holographic(
    content: str,
    *,
    source: str,
    session_id: str,
    task_id: str,
    kind: str,
    db_path: Path = HOLOGRAPHIC_DB,
) -> PlaneResult:
    memory_id = stable_memory_id(source, session_id, content)
    tags = ",".join([
        "turn-sync",
        "ob1-compatible",
        f"source:{source}",
        f"session:{session_id}",
        f"task:{task_id}",
        f"kind:{kind}",
        f"id:{memory_id}",
    ])
    try:
        with sqlite3.connect(str(db_path)) as con:
            con.execute("PRAGMA trusted_schema=ON")
            con.execute(
                """
                INSERT INTO facts(content, category, tags, trust_score)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(content) DO UPDATE SET
                    tags=excluded.tags,
                    updated_at=CURRENT_TIMESTAMP,
                    deleted_at=NULL
                """,
                (content, "turn-sync", tags, 0.82),
            )
            row = con.execute("SELECT fact_id FROM facts WHERE content = ?", (content,)).fetchone()
        return PlaneResult("holographic", True, "captured", id=str(row[0]) if row else memory_id)
    except sqlite3.Error as exc:
        return PlaneResult("holographic", False, f"capture failed: {exc}", id=memory_id)


def search_holographic(query: str, *, limit: int = 5, db_path: Path = HOLOGRAPHIC_DB) -> list[TurnMemory]:
    if not db_path.exists():
        return []
    match = fts_query(query)
    rows: list[sqlite3.Row]
    with sqlite3.connect(str(db_path)) as con:
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA trusted_schema=ON")
        if match:
            rows = con.execute(
                """
                SELECT f.fact_id, f.content, f.tags, f.trust_score, bm25(facts_fts) AS rank
                FROM facts_fts
                JOIN facts f ON f.fact_id = facts_fts.rowid
                WHERE facts_fts MATCH ? AND f.deleted_at IS NULL
                ORDER BY rank ASC
                LIMIT ?
                """,
                (match, limit),
            ).fetchall()
        else:
            rows = con.execute(
                """
                SELECT fact_id, content, tags, trust_score, 0.0 AS rank
                FROM facts
                WHERE deleted_at IS NULL
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        ids = [int(row["fact_id"]) for row in rows]
        if ids:
            try:
                con.executemany(
                    "UPDATE facts SET retrieval_count = retrieval_count + 1 WHERE fact_id = ?",
                    [(fact_id,) for fact_id in ids],
                )
            except sqlite3.OperationalError:
                pass
    memories = []
    for rank, row in enumerate(rows, 1):
        trust = float(row["trust_score"] or 0.5)
        score = (1.0 / (60 + rank)) + (trust / 100)
        memories.append(
            TurnMemory(
                plane="holographic",
                id=str(row["fact_id"]),
                content=row["content"],
                score=score,
                source="holographic",
                metadata={"tags": row["tags"], "trust_score": trust, "rank": row["rank"]},
            )
        )
    return memories
