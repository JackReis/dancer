"""tests/test_signoff.py — verify sha256 signoff."""
import subprocess
import pathlib
import tempfile
import sys
import hashlib

SCRIPT = pathlib.Path.home() / ".claude/skills/peer-grill/scripts/peer_grill_signoff.py"


def test_signoff_appends_with_correct_sha():
    tmp = pathlib.Path(tempfile.mkdtemp())
    merged = b"topic: test\nclaims: []\n"
    (tmp / "state.merged.yaml").write_bytes(merged)
    (tmp / "signoff.md").touch()
    expected_sha = hashlib.sha256(merged).hexdigest()

    r = subprocess.run(
        [sys.executable, str(SCRIPT), str(tmp), "agent-a"],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stderr

    signoff = (tmp / "signoff.md").read_text()
    assert "agent-a" in signoff
    assert expected_sha in signoff


def test_signoff_missing_merged_returns_two():
    tmp = pathlib.Path(tempfile.mkdtemp())
    (tmp / "signoff.md").touch()
    r = subprocess.run(
        [sys.executable, str(SCRIPT), str(tmp), "agent-a"],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 2, f"expected 2, got {r.returncode}: {r.stderr}"


if __name__ == "__main__":
    test_signoff_appends_with_correct_sha()
    test_signoff_missing_merged_returns_two()
    print("PASS")
