"""Regression: the MCP server must import cleanly when launched as a standalone
script (the way .mcp.json runs it) — i.e. WITHOUT conftest's sys.path injection.

Running `python3 .../quad_memory/mcp_server.py` puts the `quad_memory/` dir on
sys.path[0], not the plugin root, so `from quad_memory import ...` fails unless
the script inserts the plugin root itself. This test runs in a clean subprocess
from /tmp so it cannot rely on conftest.
"""

import subprocess
import sys
from pathlib import Path

VENV_PY = "/Users/jack.reis/Documents/=notes/.venv/bin/python3"
MCP_SERVER = Path(__file__).resolve().parents[1] / "quad_memory" / "mcp_server.py"


def test_standalone_launch_imports_cleanly():
    python = VENV_PY if Path(VENV_PY).exists() else sys.executable
    proc = subprocess.run(
        [python, str(MCP_SERVER), "--selftest"],
        cwd="/tmp",
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode == 0, f"stdout={proc.stdout!r} stderr={proc.stderr!r}"
    assert "quad-memory mcp ok" in proc.stdout
