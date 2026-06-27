"""Shared core: dataclasses + secret scrubber + id helpers.

VENDORED COPY — these symbols (SECRET_PATTERNS, reject_secret_content,
content_hash, stable_memory_id, utc_now, TurnMemory, PlaneResult) are copied
verbatim from the live SSOT:
    =notes/scripts/fleet_memory/local_turn_sync.py
Phase 2 will replace this verbatim copy with a version-pinned vendor + a drift
check (self-contained first, then hybrid). Do not edit the logic here without
re-syncing the SSOT.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


SECRET_PATTERNS = (
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\b[A-Za-z0-9_]*TOKEN[A-Za-z0-9_]*\s*=\s*\S+", re.I),
    re.compile(r"\b[A-Za-z0-9_]*KEY[A-Za-z0-9_]*\s*=\s*\S+", re.I),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
)


@dataclass(frozen=True)
class TurnMemory:
    plane: str
    id: str
    content: str
    score: float
    source: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PlaneResult:
    plane: str
    ok: bool
    detail: str
    id: str | None = None
    count: int | None = None


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def content_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def stable_memory_id(source: str, session_id: str, content: str) -> str:
    safe_source = re.sub(r"[^A-Za-z0-9_.-]+", "-", source.strip() or "fleet")
    safe_session = re.sub(r"[^A-Za-z0-9_.-]+", "-", session_id.strip() or "no-session")
    return f"{safe_source}_{safe_session}_{content_hash(content)}"


def reject_secret_content(content: str) -> None:
    for pattern in SECRET_PATTERNS:
        if pattern.search(content):
            raise ValueError("refusing to capture content that looks like a secret")
