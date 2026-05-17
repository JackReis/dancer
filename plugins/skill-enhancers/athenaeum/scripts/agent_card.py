#!/usr/bin/env python3
"""A2A Agent Card generator for Athenaeum agents."""
import json
import os
import socket
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_SKILLS = ["design", "reconcile", "ratify", "audit"]
DEFAULT_MODES = ["quick", "formal"]


def _detect_runtime() -> str:
    if os.environ.get("CLAUDE_CODE"):
        return "claude-code"
    if os.environ.get("KIMI_CLI"):
        return "kimi-cli"
    if os.environ.get("CODEX_MODE"):
        return "codex"
    return f"{os.environ.get('USER', 'agent')}-{socket.gethostname().split('.')[0]}"


def generate_card(
    name: str | None = None,
    version: str = "0.2.0",
    skills: list[str] | None = None,
    vault_root: Path | None = None,
) -> dict:
    vault = vault_root or Path.cwd()
    return {
        "name": name or os.environ.get("AGENT_NAME", _detect_runtime()),
        "description": "Athenaeum dialectic agent — design, reconcile, ratify, audit.",
        "version": version,
        "capabilities": {
            "athenaeum": {
                "skills": skills or DEFAULT_SKILLS,
                "modes": DEFAULT_MODES,
                "runtime": _detect_runtime(),
            }
        },
        "endpoints": {
            "tasks": f"file://{vault}/.athenaeum/",
            "artifacts": f"file://{vault}/.athenaeum/",
        },
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def write_card(path: Path | None = None) -> Path:
    card = generate_card()
    dest = path or (Path.cwd() / ".well-known" / "agent.json")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(card, indent=2) + "\n")
    return dest


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Generate A2A Agent Card")
    p.add_argument("--name")
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    dest = write_card(args.output)
    print(f"[agent-card] Written to {dest}")
