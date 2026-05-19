import json
import os
import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from push import push_decision


def test_push_creates_file():
    with tempfile.TemporaryDirectory() as td:
        payload = {
            "title": "Test Decision",
            "tag": "test",
            "agent": "test-agent",
            "priority": "normal",
            "decisions": [
                {"id": "opt1", "title": "Choose A or B",
                 "options": [{"key": "a", "label": "A"}, {"key": "b", "label": "B"}]}
            ]
        }
        os.environ["ARBITER_QUEUE_DIR"] = td
        result = push_decision(payload)
        assert result["status"] == "pending"
        assert result["total"] == 1
        filepath = Path(result["file"])
        assert filepath.exists()
        content = filepath.read_text()
        assert "status: pending" in content
        assert "Test Decision" in content


def test_push_with_context():
    with tempfile.TemporaryDirectory() as td:
        os.environ["ARBITER_QUEUE_DIR"] = td
        payload = {
            "title": "Risk Escalation",
            "tag": "athenaeum-audit",
            "context": "Divergent claims found",
            "priority": "high",
            "decisions": [
                {"id": "resolve", "title": "Resolution",
                 "context": "Agent A says X, Agent B says Y",
                 "options": [{"key": "a", "label": "Accept A"}, {"key": "b", "label": "Accept B"}],
                 "allowCustom": True}
            ]
        }
        result = push_decision(payload)
        assert result["status"] == "pending"
        content = Path(result["file"]).read_text()
        assert "allow_custom: true" in content
        assert "Divergent claims" in content


if __name__ == "__main__":
    test_push_creates_file()
    test_push_with_context()
    print("All tests passed!")