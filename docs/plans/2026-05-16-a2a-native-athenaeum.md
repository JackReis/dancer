# A2A-Native Athenaeum Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task.

**Goal:** Make A2A (Agent-to-Agent Protocol) a native language of the Athenaeum framework — Agent Cards for identity, Tasks as the atomic unit, typed Artifacts for durable consensus, and JSON-RPC/SSE as the live transport, while preserving filesystem durability as the persistence layer.

**Architecture:** A2A becomes the wire format and conceptual model; Athenaeum becomes an A2A extension protocol. The filesystem (`~/.athenaeum/<topic>/`) becomes a Task persistence adapter that serializes A2A Tasks and Artifacts. The Arbiter gains an A2A JSON-RPC endpoint for live interop, falling back to filesystem polling for async cross-session workflows. Each agent publishes an Agent Card describing its Athenaeum capabilities.

**Tech Stack:** Python 3 (stdlib), JSON-RPC 2.0, SSE over HTTP, YAML/JSON for filesystem persistence, Markdown for human-readable artifacts.

---

## Task 1: Add Agent Card Schema and Generator

**Files:**
- Create: `plugins/skill-enhancers/athenaeum/scripts/agent_card.py`
- Test: `plugins/skill-enhancers/athenaeum/scripts/test_agent_card.py`

**Step 1: Write the failing test**

```python
import json, tempfile, os
from pathlib import Path

def test_generate_agent_card():
    os.environ["AGENT_NAME"] = "kimi-test"
    os.environ["AGENT_RUNTIME"] = "kimi-cli"
    from agent_card import generate_card
    card = generate_card()
    assert card["name"] == "kimi-test"
    assert "athenaeum" in card["capabilities"]
    assert "design" in card["capabilities"]["athenaeum"]["skills"]
    assert card["endpoints"]["tasks"].startswith("file://")
```

**Step 2: Run test to verify it fails**

Run: `cd /tmp && python3 -c "import sys; sys.path.insert(0, 'plugins/skill-enhancers/athenaeum/scripts'); import test_agent_card; test_agent_card.test_generate_agent_card()"`

Expected: FAIL with `ModuleNotFoundError: No module named 'agent_card'`

**Step 3: Write minimal implementation**

```python
#!/usr/bin/env python3
"""A2A Agent Card generator for Athenaeum agents."""
import json, os, socket
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
```

**Step 4: Run test to verify it passes**

Run: `cd /Users/jack.reis/Documents/dancer-a2a-explore && python3 plugins/skill-enhancers/athenaeum/scripts/test_agent_card.py`

Expected: PASS

**Step 5: Commit**

```bash
git add plugins/skill-enhancers/athenaeum/scripts/agent_card.py plugins/skill-enhancers/athenaeum/scripts/test_agent_card.py
git commit -m "feat(a2a): add Agent Card generator

- generate_card() builds A2A-compliant Agent Card with Athenaeum capabilities
- write_card() persists to .well-known/agent.json
- Auto-detects runtime (Claude/Kimi/Codex) or uses AGENT_NAME env var"
```

---

## Task 2: Add A2A Task Serializer

**Files:**
- Create: `plugins/skill-enhancers/athenaeum/scripts/a2a_task.py`
- Test: `plugins/skill-enhancers/athenaeum/scripts/test_a2a_task.py`

**Step 1: Write the failing test**

```python
import json, tempfile, os
from pathlib import Path

def test_task_roundtrip():
    from a2a_task import Task, TaskStatus, save_task, load_task
    t = Task(
        id="test-001",
        session_id="sess-001",
        status=TaskStatus.SUBMITTED,
        metadata={"athenaeum_mode": "reconcile", "round_budget": 3},
    )
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        save_task(t, d)
        t2 = load_task(d / "test-001" / "task.json")
        assert t2.id == "test-001"
        assert t2.status == TaskStatus.SUBMITTED
        assert t2.metadata["athenaeum_mode"] == "reconcile"
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/jack.reis/Documents/dancer-a2a-explore && python3 plugins/skill-enhancers/athenaeum/scripts/test_a2a_task.py`

Expected: FAIL with `ModuleNotFoundError: No module named 'a2a_task'`

**Step 3: Write minimal implementation**

```python
#!/usr/bin/env python3
"""A2A Task serializer for Athenaeum workflows.

Maps Athenaeum lifecycle to A2A Task states:
  init      → submitted
  dump      → working
  grill     → input-required
  merge     → completed
  escalate   → failed
"""
from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


class TaskStatus(str, Enum):
    SUBMITTED = "submitted"
    WORKING = "working"
    INPUT_REQUIRED = "input-required"
    COMPLETED = "completed"
    CANCELED = "canceled"
    FAILED = "failed"


@dataclass
class Artifact:
    name: str
    mime_type: str
    parts: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "mimeType": self.mime_type,
            "parts": self.parts,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Artifact:
        return cls(
            name=d["name"],
            mime_type=d.get("mimeType", "text/plain"),
            parts=d.get("parts", []),
            metadata=d.get("metadata", {}),
        )


@dataclass
class Task:
    id: str
    session_id: str
    status: TaskStatus
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)
    artifacts: list[Artifact] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "sessionId": self.session_id,
            "status": self.status.value,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "metadata": self.metadata,
            "artifacts": [a.to_dict() for a in self.artifacts],
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Task:
        return cls(
            id=d["id"],
            session_id=d["sessionId"],
            status=TaskStatus(d["status"]),
            created_at=d.get("createdAt", datetime.now(timezone.utc).isoformat()),
            updated_at=d.get("updatedAt", datetime.now(timezone.utc).isoformat()),
            metadata=d.get("metadata", {}),
            artifacts=[Artifact.from_dict(a) for a in d.get("artifacts", [])],
        )


def save_task(task: Task, topic_dir: Path) -> Path:
    task_dir = topic_dir / task.id
    task_dir.mkdir(parents=True, exist_ok=True)
    task.updated_at = datetime.now(timezone.utc).isoformat()
    path = task_dir / "task.json"
    path.write_text(json.dumps(task.to_dict(), indent=2) + "\n")
    return path


def load_task(path: Path) -> Task:
    return Task.from_dict(json.loads(path.read_text()))


def init_task(
    topic: str,
    mode: str,
    session_id: str | None = None,
    round_budget: int = 3,
    formality: str = "quick",
) -> Task:
    task_id = f"athenaeum-{mode}-{topic}-{uuid.uuid4().hex[:8]}"
    return Task(
        id=task_id,
        session_id=session_id or f"{os.environ.get('USER', 'agent')}-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}",
        status=TaskStatus.SUBMITTED,
        metadata={
            "athenaeum_mode": mode,
            "topic": topic,
            "round_budget": round_budget,
            "formality": formality,
            "current_round": 0,
        },
    )
```

**Step 4: Run test to verify it passes**

Run: `cd /Users/jack.reis/Documents/dancer-a2a-explore && python3 plugins/skill-enhancers/athenaeum/scripts/test_a2a_task.py`

Expected: PASS

**Step 5: Commit**

```bash
git add plugins/skill-enhancers/athenaeum/scripts/a2a_task.py plugins/skill-enhancers/athenaeum/scripts/test_a2a_task.py
git commit -m "feat(a2a): add A2A Task serializer

- Task dataclass with A2A status mapping (submitted/working/input-required/completed/failed)
- Artifact dataclass with typed parts and metadata
- save_task/load_task for filesystem persistence in .athenaeum/<topic>/<task-id>/
- init_task() scaffolds tasks from Athenaeum mode + topic"
```

---

## Task 3: Wire A2A into `athenaeum init`

**Files:**
- Modify: `plugins/skill-enhancers/athenaeum/scripts/athenaeum` (cmd_init)
- Test: `plugins/skill-enhancers/athenaeum/scripts/test_athenaeum.py` (add tests)

**Step 1: Write the failing test**

```python
def test_init_design_creates_task_json():
    with tempfile.TemporaryDirectory() as tmp:
        os.chdir(tmp)
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "init", "test-topic", "--mode", "design"],
            capture_output=True, text=True, env={**os.environ, "KIMI_CLI": "1"}
        )
        assert result.returncode == 0
        task_path = Path(tmp) / ".athenaeum" / "test-topic" / "task.json"
        assert task_path.exists(), "task.json should exist"
        data = json.loads(task_path.read_text())
        assert data["metadata"]["athenaeum_mode"] == "design"
        assert data["status"] == "submitted"
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/jack.reis/Documents/dancer-a2a-explore && python3 plugins/skill-enhancers/athenaeum/scripts/test_athenaeum.py::AthenaeumTests::test_init_design_creates_task_json`

Expected: FAIL with `AssertionError: task.json should exist`

**Step 3: Write minimal implementation**

In `athenaeum` script, in `cmd_init`, after creating the scaffold, add:

```python
# A2A Task persistence
sys.path.insert(0, str(SCRIPT_DIR))
try:
    from a2a_task import init_task, save_task
    task = init_task(topic, mode, round_budget=3, formality=(args.ratify_mode or "quick"))
    save_task(task, ATHENAEUM_DIR / topic)
    print(f"[athenaeum] A2A Task created: {task.id}")
except Exception as exc:
    print(f"[athenaeum] A2A Task creation skipped: {exc}")
finally:
    sys.path.pop(0)
```

Add at top of file (after existing imports):

```python
import sys
```

**Step 4: Run test to verify it passes**

Run: `cd /Users/jack.reis/Documents/dancer-a2a-explore && python3 plugins/skill-enhancers/athenaeum/scripts/test_athenaeum.py::AthenaeumTests::test_init_design_creates_task_json`

Expected: PASS

**Step 5: Commit**

```bash
git add plugins/skill-enhancers/athenaeum/scripts/athenaeum plugins/skill-enhancers/athenaeum/scripts/test_athenaeum.py
git commit -m "feat(a2a): wire A2A Task creation into athenaeum init

- cmd_init now creates an A2A Task via init_task + save_task
- Task JSON lives in .athenaeum/<topic>/<task-id>/task.json
- Gracefully skips if a2a_task module is unavailable"
```

---

## Task 4: Add A2A JSON-RPC Shim to Arbiter

**Files:**
- Create: `plugins/skill-enhancers/athenaeum/scripts/a2a_rpc.py`
- Test: `plugins/skill-enhancers/athenaeum/scripts/test_a2a_rpc.py`

**Step 1: Write the failing test**

```python
import json, urllib.request

def test_tasks_send():
    from a2a_rpc import A2ARPCServer
    import threading, time
    server = A2ARPCServer(host="127.0.0.1", port=18765)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    time.sleep(0.2)

    req = urllib.request.Request(
        "http://127.0.0.1:18765/",
        data=json.dumps({
            "jsonrpc": "2.0",
            "method": "tasks/send",
            "params": {"task": {"id": "t1", "sessionId": "s1", "status": "submitted"}},
            "id": 1,
        }).encode(),
        headers={"Content-Type": "application/json"},
    )
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read())
    assert data["jsonrpc"] == "2.0"
    assert data["result"]["task"]["id"] == "t1"
    assert data["result"]["task"]["status"] == "submitted"
    server.shutdown()
```

**Step 2: Run test to verify it fails**

Run: `cd /Users/jack.reis/Documents/dancer-a2a-explore && python3 plugins/skill-enhancers/athenaeum/scripts/test_a2a_rpc.py`

Expected: FAIL with `ModuleNotFoundError: No module named 'a2a_rpc'`

**Step 3: Write minimal implementation**

```python
#!/usr/bin/env python3
"""A2A JSON-RPC 2.0 shim for Athenaeum live interop.

Implements:
  tasks/send     — create or update a Task
  tasks/get      — retrieve a Task by ID
  tasks/cancel   — cancel a Task
  tasks/sendSubscribe — SSE stream of Task updates (stub)

Tasks are persisted to filesystem (.athenaeum/<topic>/<task-id>/).
"""
from __future__ import annotations

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR))
from a2a_task import Task, TaskStatus, save_task, load_task  # noqa: E402

VAULT_ROOT = Path(os.environ.get("ATHENAEUM_VAULT", Path.cwd()))
TASKS_ROOT = VAULT_ROOT / ".athenaeum"


class A2AHandler(BaseHTTPRequestHandler):
    server_version = "athenaeum-a2a/0.1"

    def _send_json(self, status: int, body: dict[str, Any]) -> None:
        payload = json.dumps(body, separators=(",", ":")).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length <= 0 or length > 1_048_576:
            self._send_json(400, {"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": None})
            return
        raw = self.rfile.read(length)
        try:
            req = json.loads(raw)
        except json.JSONDecodeError:
            self._send_json(400, {"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": None})
            return

        req_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})

        try:
            result = self._dispatch(method, params)
            self._send_json(200, {"jsonrpc": "2.0", "result": result, "id": req_id})
        except Exception as exc:
            self._send_json(200, {"jsonrpc": "2.0", "error": {"code": -32603, "message": str(exc)}, "id": req_id})

    def _dispatch(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        if method == "tasks/send":
            return self._tasks_send(params)
        if method == "tasks/get":
            return self._tasks_get(params)
        if method == "tasks/cancel":
            return self._tasks_cancel(params)
        raise ValueError(f"Method not found: {method}")

    def _tasks_send(self, params: dict[str, Any]) -> dict[str, Any]:
        task_data = params.get("task", {})
        task = Task.from_dict(task_data)
        topic = task.metadata.get("topic", "default")
        save_task(task, TASKS_ROOT / topic)
        return {"task": task.to_dict()}

    def _tasks_get(self, params: dict[str, Any]) -> dict[str, Any]:
        task_id = params.get("id")
        topic = params.get("topic", "default")
        path = TASKS_ROOT / topic / task_id / "task.json"
        if not path.exists():
            raise ValueError(f"Task not found: {task_id}")
        task = load_task(path)
        return {"task": task.to_dict()}

    def _tasks_cancel(self, params: dict[str, Any]) -> dict[str, Any]:
        task_id = params.get("id")
        topic = params.get("topic", "default")
        path = TASKS_ROOT / topic / task_id / "task.json"
        if not path.exists():
            raise ValueError(f"Task not found: {task_id}")
        task = load_task(path)
        task.status = TaskStatus.CANCELED
        save_task(task, TASKS_ROOT / topic)
        return {"task": task.to_dict()}

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        return


class A2ARPCServer(ThreadingHTTPServer):
    allow_reuse_address = True


def main() -> int:
    host = os.environ.get("ATHENAEUM_A2A_HOST", "127.0.0.1")
    port = int(os.environ.get("ATHENAEUM_A2A_PORT", "18765"))
    server = A2ARPCServer((host, port), A2AHandler)
    print(f"[a2a-rpc] Listening on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

**Step 4: Run test to verify it passes**

Run: `cd /Users/jack.reis/Documents/dancer-a2a-explore && python3 plugins/skill-enhancers/athenaeum/scripts/test_a2a_rpc.py`

Expected: PASS

**Step 5: Commit**

```bash
git add plugins/skill-enhancers/athenaeum/scripts/a2a_rpc.py plugins/skill-enhancers/athenaeum/scripts/test_a2a_rpc.py
git commit -m "feat(a2a): add JSON-RPC 2.0 shim for live A2A interop

- Implements tasks/send, tasks/get, tasks/cancel
- Tasks persisted to filesystem (.athenaeum/<topic>/<task-id>/)
- Binds to ATHENAEUM_A2A_HOST:ATHENAEUM_A2A_PORT (default 127.0.0.1:18765)"
```

---

## Task 5: Update SKILL.md Files with A2A Vocabulary

**Files:**
- Modify: `plugins/skill-enhancers/athenaeum/athenaeum-design/SKILL.md`
- Modify: `plugins/skill-enhancers/athenaeum/athenaeum-reconcile/SKILL.md`
- Modify: `plugins/skill-enhancers/athenaeum/athenaeum-ratify/SKILL.md`
- Modify: `plugins/skill-enhancers/athenaeum/athenaeum-audit/SKILL.md`

**Step 1: Read current SKILL.md files**

Each is ~50-60 lines. Add an A2A section at the bottom (before "Sibling skills"):

```markdown
## A2A interop

This skill speaks A2A natively. An A2A Task represents this workflow.

**Task metadata:**
- `athenaeum_mode: design`
- `status` lifecycle: `submitted` → `working` → `input-required` → `completed`

**Artifacts produced:**
- `DESIGN.md` — `text/markdown`
- `AGENT_DESIGN.md` — `text/markdown` (agent-stack audits)

**Invoking via A2A:**
```json
{
  "jsonrpc": "2.0",
  "method": "tasks/send",
  "params": {
    "task": {
      "id": "athenaeum-design-my-topic",
      "sessionId": "<agent-session>",
      "status": "submitted",
      "metadata": {"athenaeum_mode": "design", "topic": "my-topic"}
    }
  }
}
```
```

(Adjust `athenaeum_mode` and Artifacts per skill: `reconcile`, `ratify`, `audit`.)

**Step 2: No failing test needed** — docs change only. Verify rendered markdown:

Run: `python3 -c "import markdown; ..."` or just open in a Markdown viewer.

**Step 3: Commit**

```bash
git add plugins/skill-enhancers/athenaeum/athenaeum-design/SKILL.md plugins/skill-enhancers/athenaeum/athenaeum-reconcile/SKILL.md plugins/skill-enhancers/athenaeum/athenaeum-ratify/SKILL.md plugins/skill-enhancers/athenaeum/athenaeum-audit/SKILL.md
git commit -m "docs(a2a): add A2A interop section to all 4 SKILL.md files

- Task metadata, status lifecycle, Artifacts produced
- JSON-RPC invocation examples per mode"
```

---

## Task 6: Write A2A-Native REFERENCE.md Extension

**Files:**
- Create: `plugins/skill-enhancers/athenaeum/REFERENCE-A2A.md`

**Step 1: Write document**

```markdown
# Athenaeum — A2A Native Reference

Deep protocol docs for A2A-native Athenaeum workflows.

## §A1 A2A status mapping

| Athenaeum phase | A2A TaskStatus | Trigger |
|---|---|---|
| `init` | `submitted` | Task created via `tasks/send` |
| `dump` | `working` | Agent writes `.claims.yaml` Artifact |
| `grill` | `input-required` | Lower-confidence agent must answer |
| `merge` | `completed` | `state.merged.yaml` ratified |
| `escalate` | `failed` | Round budget exhausted |
| `human-grain-gate` | `input-required` | Human fills `human-decision.yaml` |
| `sign` | `completed` | SHA-256 signoff appended |

## §A2 Artifact types

| Artifact name | MIME type | Writers | Description |
|---|---|---|---|
| `<agent>.claims.yaml` | `application/yaml` | one agent | Self-reported state dump |
| `diff.md` | `text/markdown` | last writer | Three-bucket diff |
| `grill-log.md` | `text/markdown` | append-only | Q&A transcript |
| `state.merged.yaml` | `application/yaml` | merge writer | Converged ground truth |
| `signoff.md` | `text/markdown` | append-only | SHA-256 attestation |
| `artifact.md` | `text/markdown` | initiator | Frozen artifact (ratify) |
| `<agent>.vote.yaml` | `application/yaml` | one agent | SIGN / DISSENT |
| `manifest.yaml` | `application/yaml` | initiator | Roster + expires_at |
| `audit-report.md` | `text/markdown` | auditor | 13-branch findings |

## §A3 JSON-RPC endpoints

### `tasks/send`

Create or update a Task. Tasks are idempotent by ID.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "tasks/send",
  "params": {
    "task": {
      "id": "athenaeum-reconcile-pricing-abc123",
      "sessionId": "kimi-mac-jr-20260516-001",
      "status": "submitted",
      "metadata": {
        "athenaeum_mode": "reconcile",
        "topic": "pricing-decisions",
        "round_budget": 3,
        "formality": "quick"
      },
      "artifacts": [
        {"name": "claims-template", "mimeType": "application/yaml", "parts": [{"type": "text", "text": "agent: <your-agent-name>\nclaims:\n  - id: <slug>\n    statement: <one sentence>\n    confidence: medium\n    source: <file:line>"}]}
      ]
    }
  },
  "id": 1
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "task": {
      "id": "athenaeum-reconcile-pricing-abc123",
      "sessionId": "kimi-mac-jr-20260516-001",
      "status": "submitted",
      "createdAt": "2026-05-16T19:35:00+00:00",
      "updatedAt": "2026-05-16T19:35:00+00:00",
      "metadata": {...},
      "artifacts": [...]
    }
  },
  "id": 1
}
```

### `tasks/get`

Retrieve a Task by ID.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "tasks/get",
  "params": {"id": "athenaeum-reconcile-pricing-abc123", "topic": "pricing-decisions"},
  "id": 2
}
```

### `tasks/cancel`

Cancel a Task.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "tasks/cancel",
  "params": {"id": "athenaeum-reconcile-pricing-abc123", "topic": "pricing-decisions"},
  "id": 3
}
```

## §A4 Agent Card example

```json
{
  "name": "claude-code-mac-jr",
  "description": "Athenaeum dialectic agent — design, reconcile, ratify, audit.",
  "version": "0.2.0",
  "capabilities": {
    "athenaeum": {
      "skills": ["design", "reconcile", "ratify", "audit"],
      "modes": ["quick", "formal"],
      "runtime": "claude-code"
    }
  },
  "endpoints": {
    "tasks": "file:///Users/jack.reis/Documents/dancer/.athenaeum/",
    "artifacts": "file:///Users/jack.reis/Documents/dancer/.athenaeum/"
  }
}
```

## §A5 Coexistence with non-A2A agents

A2A-native Athenaeum agents can interoperate with filesystem-only agents:

- A2A agent creates Task → filesystem agent reads `task.json` and acts
- Filesystem agent writes YAML → A2A agent polls `tasks/get` for updates
- The Arbiter can translate between A2A JSON-RPC and filesystem events

No agent is required to implement A2A. The filesystem is the floor.
```

**Step 2: Commit**

```bash
git add plugins/skill-enhancers/athenaeum/REFERENCE-A2A.md
git commit -m "docs(a2a): add A2A-native reference protocol

- Status mapping, Artifact types, JSON-RPC endpoints
- Agent Card example, coexistence with non-A2A agents"
```

---

## Task 7: Run Full Test Suite

**Files:**
- All test files created above

**Step 1: Run all tests**

```bash
cd /Users/jack.reis/Documents/dancer-a2a-explore/plugins/skill-enhancers/athenaeum/scripts
python3 test_agent_card.py
python3 test_a2a_task.py
python3 test_athenaeum.py
python3 test_a2a_rpc.py
```

**Step 2: Verify all pass**

Expected: 4 suites, all PASS.

**Step 3: Commit**

```bash
git add -A
git commit -m "test(a2a): run full test suite — all pass

- agent_card, a2a_task, athenaeum (existing + new), a2a_rpc
- No regressions in existing functionality"
```

---

## Execution Handoff

**Plan complete and saved to `docs/plans/2026-05-16-a2a-native-athenaeum.md`.**

**Two execution options:**

1. **Subagent-Driven (this session)** — I dispatch fresh subagent per task, review between tasks, fast iteration

2. **Parallel Session (separate)** — Open new session in worktree, batch execution with checkpoints

**Which approach?**
