import sqlite3

import pytest


def _init_schema(db_path):
    """Create the minimal `facts` + `facts_fts` schema the plane expects."""
    with sqlite3.connect(str(db_path)) as con:
        con.executescript(
            """
            CREATE TABLE facts (
                fact_id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT UNIQUE,
                category TEXT,
                tags TEXT,
                trust_score REAL DEFAULT 0.5,
                retrieval_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                deleted_at TIMESTAMP
            );
            CREATE VIRTUAL TABLE facts_fts USING fts5(content, content='facts', content_rowid='fact_id');
            CREATE TRIGGER facts_ai AFTER INSERT ON facts BEGIN
                INSERT INTO facts_fts(rowid, content) VALUES (new.fact_id, new.content);
            END;
            CREATE TRIGGER facts_au AFTER UPDATE ON facts BEGIN
                INSERT INTO facts_fts(facts_fts, rowid, content) VALUES('delete', old.fact_id, old.content);
                INSERT INTO facts_fts(rowid, content) VALUES (new.fact_id, new.content);
            END;
            """
        )


def test_holographic_roundtrip(tmp_path):
    from quad_memory.holographic import capture_holographic, search_holographic, holographic_health
    db = tmp_path / "h.db"
    _init_schema(db)
    r = capture_holographic("verified handoff for quad-memory", source="claude-code",
                            session_id="s1", task_id="t1", kind="turn_fact", db_path=db)
    assert r.ok
    hits = search_holographic("handoff", limit=5, db_path=db)
    assert any("quad-memory" in m.content for m in hits)
    assert holographic_health(db_path=db).ok


def test_holographic_health_missing_db(tmp_path):
    from quad_memory.holographic import holographic_health
    r = holographic_health(db_path=tmp_path / "nope.db")
    assert r.ok is False and "missing db" in r.detail


def test_search_missing_db_returns_empty(tmp_path):
    from quad_memory.holographic import search_holographic
    assert search_holographic("anything", db_path=tmp_path / "nope.db") == []
