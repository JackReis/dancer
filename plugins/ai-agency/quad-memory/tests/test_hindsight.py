import json
from unittest.mock import patch


class FakeResp:
    def __init__(self, status, body):
        self.status = status
        self._body = json.dumps(body).encode("utf-8")

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_capture_posts_wellformed_record():
    from quad_memory.hindsight import capture_hindsight
    captured = {}

    def fake_urlopen(req, timeout=None):
        captured["url"] = req.full_url
        captured["method"] = req.get_method()
        captured["data"] = json.loads(req.data)
        return FakeResp(202, {"status": "submitted"})

    with patch("urllib.request.urlopen", fake_urlopen):
        r = capture_hindsight("verified handoff for quad-memory plugin", source="claude-code",
                              session_id="s1", task_id="t1", kind="turn_fact")
    assert r.ok
    assert captured["method"] == "POST"
    assert captured["url"].endswith("/memories")
    item = captured["data"]["items"][0]
    assert item["content"] == "verified handoff for quad-memory plugin"
    assert "turn-sync" in item["tags"]
    assert item["metadata"]["source"] == "claude-code"


def test_recall_parses_results():
    from quad_memory.hindsight import recall_hindsight
    body = {"results": [
        {"text": "Jack prefers local-first", "id": "m1", "type": "world", "context": "pref"},
        {"content": "second fact", "document_id": "m2", "type": "experience"},
    ]}

    def fake_urlopen(req, timeout=None):
        return FakeResp(200, body)

    with patch("urllib.request.urlopen", fake_urlopen):
        mems = recall_hindsight("what does Jack prefer?", limit=5)
    assert len(mems) == 2
    assert mems[0].plane == "hindsight"
    assert mems[0].content == "Jack prefers local-first"
    assert mems[0].id == "m1"


def test_recall_fails_open_on_error():
    from quad_memory.hindsight import recall_hindsight

    def boom(req, timeout=None):
        raise OSError("connection refused")

    with patch("urllib.request.urlopen", boom):
        assert recall_hindsight("anything") == []


def test_classify_retention_drops_short_ephemeral():
    from quad_memory.hindsight import classify_retention
    assert classify_retention("hi", "claude-code").retain is False
    assert classify_retention("blocked", "claude-code").retain is True
    assert classify_retention("a much longer durable observation here", "claude-code").retain is True
