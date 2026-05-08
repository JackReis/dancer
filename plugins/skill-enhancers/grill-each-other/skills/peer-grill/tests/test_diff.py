"""tests/test_diff.py — verify three-bucket diff."""
import subprocess
import pathlib
import shutil
import tempfile
import sys

CANDIDATE_PYTHONS = [
    sys.executable,
    "/usr/bin/python3",
    "/opt/homebrew/bin/python3",
    str(pathlib.Path.home() / ".mcp-venv/bin/python3"),
]


def python_with_yaml():
    for py in CANDIDATE_PYTHONS:
        try:
            r = subprocess.run([py, "-c", "import yaml"], capture_output=True)
            if r.returncode == 0:
                return py
        except (FileNotFoundError, OSError):
            continue
    return None


SKILL = pathlib.Path.home() / ".claude/skills/peer-grill"


def test_diff_three_buckets():
    py = python_with_yaml()
    if py is None:
        print("SKIP: PyYAML not found; install via `pip install pyyaml`")
        return
    tmpdir = pathlib.Path(tempfile.mkdtemp())
    fixture = SKILL / "tests/fixtures/two-claims"
    for name in ("agent-a.claims.yaml", "agent-b.claims.yaml"):
        shutil.copy(fixture / name, tmpdir / name)
    (tmpdir / "diff.md").touch()

    script = SKILL / "scripts/peer_grill_diff.py"
    r = subprocess.run(
        [py, str(script), str(tmpdir)], capture_output=True, text=True
    )
    assert r.returncode == 0, r.stderr

    diff = (tmpdir / "diff.md").read_text()
    assert "DISAGREED" in diff and "db-version" in diff, diff
    assert "ONLY agent-a" in diff and "deploy-script" in diff, diff
    assert "ONLY agent-b" in diff and "monitoring" in diff, diff
    shutil.rmtree(tmpdir)


if __name__ == "__main__":
    test_diff_three_buckets()
    print("PASS")
