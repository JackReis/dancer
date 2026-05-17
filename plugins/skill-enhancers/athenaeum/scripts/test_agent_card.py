import json, os, sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR))


def test_generate_agent_card():
    os.environ["AGENT_NAME"] = "kimi-test"
    os.environ["AGENT_RUNTIME"] = "kimi-cli"
    from agent_card import generate_card
    card = generate_card()
    assert card["name"] == "kimi-test"
    assert "athenaeum" in card["capabilities"]
    assert "design" in card["capabilities"]["athenaeum"]["skills"]
    assert card["endpoints"]["tasks"].startswith("file://")


def test_write_card():
    import tempfile
    from agent_card import write_card
    with tempfile.TemporaryDirectory() as tmp:
        dest = write_card(Path(tmp) / "agent.json")
        assert dest.exists()
        data = json.loads(dest.read_text())
        assert "name" in data
        assert "capabilities" in data


if __name__ == "__main__":
    test_generate_agent_card()
    test_write_card()
    print("[test_agent_card] PASS")
