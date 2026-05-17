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
