#!/usr/bin/env python3
"""arbiter_push — Create a decision plan for human review via Arbiter Zebu."""

import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

QUEUE_DIR = Path(os.environ.get("ARBITER_QUEUE_DIR", Path.home() / ".arbiter" / "queue"))


def push_decision(payload: dict) -> dict:
    plan_id = uuid.uuid4().hex[:8]
    agent = payload.get("agent", os.environ.get("CLAWDBOT_AGENT", "unknown"))
    session = payload.get("session", os.environ.get("CLAWDBOT_SESSION", ""))
    tag = payload.get("tag", "general")
    title = payload["title"]
    priority = payload.get("priority", "normal")
    context = payload.get("context", "")
    notify = payload.get("notify", "")
    decisions = payload.get("decisions", [])

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    frontmatter = {
        "id": plan_id, "version": 1, "agent": agent, "session": session,
        "tag": tag, "title": title, "priority": priority,
        "status": "pending", "created_at": now, "updated_at": now,
        "completed_at": None, "total": len(decisions),
        "answered": 0, "remaining": len(decisions),
        "notify_session": notify,
    }

    fm_lines = "---\n"
    for k, v in frontmatter.items():
        fm_lines += f"{k}: {v}\n"
    fm_lines += "---\n\n"

    body = f"# {title}\n\n{context}\n\n---\n\n"
    for i, dec in enumerate(decisions, 1):
        body += f"## Decision {i}: {dec['title']}\n\n"
        body += f"id: {dec['id']}\n"
        body += f"status: pending\nanswer: null\nanswered_at: null\n"
        if dec.get("allowCustom"):
            body += f"allow_custom: true\n"
        body += f"\n**Context:** {dec.get('context', '')}\n\n"
        body += "**Options:**\n"
        for opt in dec.get("options", []):
            note = f" ({opt['note']})" if opt.get("note") else ""
            body += f"- `{opt['key']}` — {opt['label']}{note}\n"
        body += "\n---\n\n"

    pending_dir = QUEUE_DIR / "pending"
    pending_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{agent}-{tag}-{plan_id}.md"
    filepath = pending_dir / filename
    filepath.write_text(fm_lines + body, encoding="utf-8")

    return {
        "planId": plan_id,
        "file": str(filepath),
        "total": len(decisions),
        "status": "pending",
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: arbiter-push '<json>'", file=sys.stderr)
        sys.exit(1)
    payload = json.loads(sys.argv[1])
    result = push_decision(payload)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()