"""OBn plane — Chroma vault-ingest semantic search.

VENDORED COPY — `obn_health`, `capture_obn`, `search_obn`,
`parse_obn_federated_text`, `obn_memory_from_parsed` are copied verbatim from
the live SSOT =notes/scripts/fleet_memory/local_turn_sync.py with one
adaptation: every vault path default is now env-overridable (VAULT_ROOT,
OBN_CAPTURE, OBN_INGEST_DIR, OBN_CHROMA_DIR, VAULT_VENV_PYTHON) so the plugin
degrades gracefully when the vault is absent (e.g. on Aegis).
Phase 2 will replace this verbatim copy with a version-pinned vendor + drift
check.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from quad_memory.core import TurnMemory, PlaneResult


VAULT_ROOT = Path(os.environ.get("VAULT_ROOT", "/Users/jack.reis/Documents/=notes"))
OBN_CAPTURE = Path(os.environ.get("OBN_CAPTURE", Path.home() / ".claude" / "scripts" / "obn_capture_thought.py"))
OBN_INGEST_DIR = Path(os.environ.get("OBN_INGEST_DIR", VAULT_ROOT / "claude" / "scheduled-tasks" / "vault-ingest"))
OBN_CHROMA_DIR = Path(os.environ.get("OBN_CHROMA_DIR", OBN_INGEST_DIR / "chroma_db"))
VAULT_VENV_PYTHON = Path(os.environ.get("VAULT_VENV_PYTHON", VAULT_ROOT / ".venv" / "bin" / "python3"))


def obn_health() -> PlaneResult:
    if not OBN_CHROMA_DIR.exists():
        return PlaneResult("obn", False, f"missing Chroma dir: {OBN_CHROMA_DIR}")
    python = VAULT_VENV_PYTHON if VAULT_VENV_PYTHON.exists() else Path(sys.executable)
    try:
        proc = subprocess.run(
            [str(python), str(OBN_INGEST_DIR / "obn_query.py"), "--pods"],
            check=False,
            capture_output=True,
            text=True,
            timeout=20,
        )
    except Exception as exc:
        return PlaneResult("obn", False, f"health failed: {exc}")
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip().splitlines()[:1]
        return PlaneResult("obn", False, detail[0] if detail else "obn_query failed")
    count = sum(1 for line in proc.stdout.splitlines() if "(" in line and "docs" in line)
    return PlaneResult("obn", True, "Chroma pods queryable", count=count)


def capture_obn(content: str, *, source: str, session_id: str, kind: str) -> PlaneResult:
    if not OBN_CAPTURE.exists():
        return PlaneResult("obn", False, f"missing capture script: {OBN_CAPTURE}")
    python = VAULT_VENV_PYTHON if VAULT_VENV_PYTHON.exists() else Path(sys.executable)
    try:
        proc = subprocess.run(
            [
                str(python),
                str(OBN_CAPTURE),
                content,
                "--session-id",
                session_id,
                "--source",
                source,
                "--kind",
                kind,
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=90,
        )
    except Exception as exc:
        return PlaneResult("obn", False, f"capture failed: {exc}")
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip().splitlines()[:1]
        return PlaneResult("obn", False, detail[0] if detail else "OBn capture failed")
    try:
        body = json.loads(proc.stdout)
    except json.JSONDecodeError:
        body = {}
    return PlaneResult("obn", True, body.get("status", "captured"), id=body.get("doc_id"))


def search_obn(query: str, *, limit: int = 5) -> list[TurnMemory]:
    python = VAULT_VENV_PYTHON if VAULT_VENV_PYTHON.exists() else Path(sys.executable)
    script = OBN_INGEST_DIR / "obn_query.py"
    if not script.exists():
        return []
    try:
        proc = subprocess.run(
            [str(python), str(script), query, "--federated", "--n", str(limit)],
            check=False,
            capture_output=True,
            text=True,
            timeout=90,
        )
    except Exception:
        return []
    if proc.returncode != 0:
        return []
    return parse_obn_federated_text(proc.stdout)


def parse_obn_federated_text(text: str) -> list[TurnMemory]:
    memories: list[TurnMemory] = []
    current: dict[str, Any] | None = None
    for line in text.splitlines():
        stripped = line.strip()
        header = re.match(r"^\d+\.\s+\[(?P<pod>[^\]]+)\]\s+(?P<path>.+)$", stripped)
        if header:
            if current and current.get("content"):
                memories.append(obn_memory_from_parsed(current, len(memories) + 1))
            current = {"pod": header.group("pod"), "path": header.group("path"), "distance": None, "content": ""}
            continue
        if current is None:
            continue
        if stripped.startswith("Distance:"):
            try:
                current["distance"] = float(stripped.split(":", 1)[1].strip())
            except ValueError:
                current["distance"] = None
        elif stripped:
            current["content"] += (" " if current["content"] else "") + stripped.removesuffix("...")
    if current and current.get("content"):
        memories.append(obn_memory_from_parsed(current, len(memories) + 1))
    return memories


def obn_memory_from_parsed(parsed: dict[str, Any], rank: int) -> TurnMemory:
    distance = parsed.get("distance")
    semantic_score = 1.0 / (1.0 + float(distance)) if isinstance(distance, float) else 0.0
    return TurnMemory(
        plane="obn",
        id=f"{parsed.get('pod')}:{parsed.get('path')}",
        content=parsed.get("content", ""),
        score=(1.0 / (60 + rank)) + (semantic_score / 100),
        source="obn",
        metadata={"pod": parsed.get("pod"), "vault_path": parsed.get("path"), "distance": distance},
    )
