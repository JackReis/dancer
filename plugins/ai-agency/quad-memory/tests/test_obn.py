import json
from types import SimpleNamespace

import pytest

# A real `obn_query.py --federated` output sample (format from
# =notes/claude/scheduled-tasks/vault-ingest/obn_query.py:215-223).
FEDERATED_SAMPLE = '''
Federated Query: "handoff"
============================================================

1. [core] daily/2026-06-25.md
   Distance: 0.1234
   verified handoff for quad-memory plugin work today...

2. [health] atlas/health/pt-sessions-ryan.md
   Distance: 0.4567
   PT session notes; discharged 2026-03-20...
'''


def test_parse_obn_federated_text():
    from quad_memory.obn import parse_obn_federated_text
    mems = parse_obn_federated_text(FEDERATED_SAMPLE)
    assert len(mems) == 2
    assert mems[0].plane == "obn"
    assert mems[0].metadata["pod"] == "core"
    assert mems[0].metadata["vault_path"] == "daily/2026-06-25.md"
    assert mems[0].metadata["distance"] == 0.1234
    assert "verified handoff" in mems[0].content
    assert not mems[0].content.endswith("...")
    assert mems[1].metadata["pod"] == "health"


def test_search_obn_mocks_subprocess(monkeypatch):
    import quad_memory.obn as obn

    def fake_run(cmd, **kwargs):
        return SimpleNamespace(returncode=0, stdout=FEDERATED_SAMPLE, stderr="")

    # Point script path at an existing file so the existence guard passes.
    monkeypatch.setattr(obn, "OBN_INGEST_DIR", obn.OBN_INGEST_DIR)
    monkeypatch.setattr(obn.subprocess, "run", fake_run)
    # Ensure the query script existence check passes regardless of host.
    monkeypatch.setattr(obn.Path, "exists", lambda self: True)
    mems = obn.search_obn("handoff", limit=5)
    assert len(mems) == 2 and mems[0].plane == "obn"


def test_capture_obn_mocks_subprocess(monkeypatch, tmp_path):
    import quad_memory.obn as obn

    script = tmp_path / "obn_capture_thought.py"
    script.write_text("# stub")
    monkeypatch.setattr(obn, "OBN_CAPTURE", script)

    def fake_run(cmd, **kwargs):
        return SimpleNamespace(returncode=0, stdout=json.dumps({"status": "captured", "doc_id": "d1"}), stderr="")

    monkeypatch.setattr(obn.subprocess, "run", fake_run)
    r = obn.capture_obn("verified handoff", source="claude-code", session_id="s1", kind="turn_fact")
    assert r.ok and r.id == "d1"


def test_capture_obn_missing_script(monkeypatch, tmp_path):
    import quad_memory.obn as obn
    monkeypatch.setattr(obn, "OBN_CAPTURE", tmp_path / "nope.py")
    r = obn.capture_obn("x", source="claude-code", session_id="s1", kind="turn_fact")
    assert r.ok is False and "missing capture script" in r.detail
