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
import os
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
