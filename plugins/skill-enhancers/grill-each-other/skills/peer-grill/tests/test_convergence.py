"""tests/test_convergence.py — verify convergence detection in both formats."""
import subprocess
import pathlib
import tempfile
import sys

SCRIPT = pathlib.Path.home() / ".claude/skills/peer-grill/scripts/peer_grill_check_convergence.py"


def test_both_ratified_inline_format_returns_zero():
    tmp = pathlib.Path(tempfile.mkdtemp())
    (tmp / "grill-log.md").write_text(
        "[2026-05-03T00:00:00Z] agent-a -> agent-b | claim:db-version | RATIFY: db-version | postgres 15.6\n"
        "[2026-05-03T00:01:00Z] agent-b -> agent-a | claim:db-version | RATIFY: db-version | postgres 15.6\n"
    )
    r = subprocess.run(
        [sys.executable, str(SCRIPT), str(tmp), "db-version"],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, f"expected 0, got {r.returncode}: {r.stdout} {r.stderr}"


def test_both_ratified_standalone_format_returns_zero():
    """Matches the matrix-mcp-shim-path fixture format."""
    tmp = pathlib.Path(tempfile.mkdtemp())
    (tmp / "grill-log.md").write_text(
        "[2026-05-03T00:00:00Z] claude-stytch-advocate\n"
        "RATIFY: oauth-dcr-required | claude.ai requires DCR\n"
        "RATIFY: db-version | postgres 15.6\n"
        "\n"
        "[2026-05-03T00:00:30Z] claude-ngrok-advocate\n"
        "RATIFY: oauth-dcr-required | claude.ai requires DCR\n"
        "RATIFY: db-version | postgres 15.6\n"
    )
    r = subprocess.run(
        [sys.executable, str(SCRIPT), str(tmp), "db-version"],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, f"expected 0, got {r.returncode}: {r.stdout} {r.stderr}"


def test_one_ratified_returns_one():
    tmp = pathlib.Path(tempfile.mkdtemp())
    (tmp / "grill-log.md").write_text(
        "[2026-05-03T00:00:00Z] agent-a -> agent-b | claim:db-version | RATIFY: db-version | postgres 15.6\n"
    )
    r = subprocess.run(
        [sys.executable, str(SCRIPT), str(tmp), "db-version"],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 1, f"expected 1, got {r.returncode}"


if __name__ == "__main__":
    test_both_ratified_inline_format_returns_zero()
    test_both_ratified_standalone_format_returns_zero()
    test_one_ratified_returns_one()
    print("PASS")
