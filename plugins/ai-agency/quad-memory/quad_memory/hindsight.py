"""Hindsight plane — HTTP memory daemon (semantic recall).

VENDORED COPY:
  - `http_json`, `hindsight_health`, `capture_hindsight`, `recall_hindsight`
    copied verbatim from =notes/scripts/fleet_memory/local_turn_sync.py
  - `VALID_NETWORKS`, `RetentionDecision`, `MemoryUnit`, `classify_retention`
    copied verbatim from =notes/scripts/fleet_memory/hindsight.py
Env wiring preserved: HINDSIGHT_URL (HINDSIGHT_URL | HINDSIGHT_API_URL |
http://127.0.0.1:9177), HINDSIGHT_BANK (default `hermes`).
Phase 2 will replace this verbatim copy with a version-pinned vendor + drift
check.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any

from quad_memory.core import TurnMemory, PlaneResult, content_hash, stable_memory_id, utc_now


# Honor the fleet-standard HINDSIGHT_API_URL (set in ~/.hermes/.env) as the primary
# source; fall back to the legacy HINDSIGHT_URL, then to the live daemon port :9177.
HINDSIGHT_URL = (
    os.environ.get("HINDSIGHT_URL")
    or os.environ.get("HINDSIGHT_API_URL")
    or "http://127.0.0.1:9177"
)
HINDSIGHT_BANK = os.environ.get("HINDSIGHT_BANK", "hermes")


VALID_NETWORKS = {"world", "experience", "opinion", "observation"}


@dataclass(frozen=True)
class RetentionDecision:
    retain: bool
    reason: str


@dataclass(frozen=True)
class MemoryUnit:
    id: str
    network_type: str
    agent_id: str
    text: str
    confidence: float
    entities: list[str]
    source_system: str
    source_uri: str
    metadata: dict[str, Any] = field(default_factory=dict)
    embedding: list[float] | None = None

    def to_record(self) -> dict[str, Any]:
        if self.network_type not in VALID_NETWORKS:
            raise ValueError(f"invalid network_type: {self.network_type}")
        if not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")
        return {
            "id": self.id,
            "network_type": self.network_type,
            "agent_id": self.agent_id,
            "text": self.text,
            "confidence": self.confidence,
            "entities": self.entities,
            "source_system": self.source_system,
            "source_uri": self.source_uri,
            "metadata": self.metadata,
            "embedding": self.embedding,
        }


def classify_retention(text: str, source_system: str) -> RetentionDecision:
    normalized = text.strip().lower()
    durable_terms = (
        "blocked",
        "closed",
        "commit",
        "failed",
        "handoff",
        "reachable",
        "verified",
    )
    if len(normalized) < 20 and not any(term in normalized for term in durable_terms):
        return RetentionDecision(retain=False, reason="ephemeral")
    return RetentionDecision(retain=True, reason="durable_candidate")


def http_json(method: str, url: str, payload: dict[str, Any] | None = None, timeout: int = 10) -> tuple[int, dict[str, Any]]:
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            body = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            body = {"error": raw}
        return exc.code, body


def hindsight_health(base_url: str = HINDSIGHT_URL, bank: str = HINDSIGHT_BANK) -> PlaneResult:
    try:
        code, _body = http_json("GET", f"{base_url}/health", timeout=3)
        if code < 200 or code >= 300:
            return PlaneResult("hindsight", False, f"health HTTP {code}")
        code, body = http_json("GET", f"{base_url}/v1/default/banks", timeout=3)
        count = None
        if code >= 200 and code < 300:
            for item in body.get("banks", []):
                if item.get("bank_id") == bank:
                    count = item.get("fact_count")
                    break
        return PlaneResult("hindsight", True, "api reachable", count=count)
    except Exception as exc:
        return PlaneResult("hindsight", False, f"unreachable: {exc}")


def capture_hindsight(
    content: str,
    *,
    source: str,
    session_id: str,
    task_id: str,
    kind: str,
    base_url: str = HINDSIGHT_URL,
    bank: str = HINDSIGHT_BANK,
) -> PlaneResult:
    memory_id = stable_memory_id(source, session_id, content)
    payload = {
        "async": True,
        "items": [
            {
                "content": content,
                "context": "per-turn sync",
                "document_id": memory_id,
                "tags": ["turn-sync", "ob1-compatible", source, kind],
                "metadata": {
                    "source": source,
                    "session_id": session_id,
                    "task_id": task_id,
                    "kind": kind,
                    "content_hash": content_hash(content),
                    "captured_at": utc_now(),
                },
            }
        ],
    }
    try:
        code, body = http_json("POST", f"{base_url}/v1/default/banks/{bank}/memories", payload, timeout=30)
        if 200 <= code < 300:
            detail = f"accepted HTTP {code}"
            if isinstance(body, dict) and body:
                detail = f"{detail}: {body.get('status') or body.get('message') or 'submitted'}"
            return PlaneResult("hindsight", True, detail, id=memory_id)
        return PlaneResult("hindsight", False, f"retain HTTP {code}", id=memory_id)
    except Exception as exc:
        return PlaneResult("hindsight", False, f"retain failed: {exc}", id=memory_id)


def recall_hindsight(
    query: str,
    *,
    limit: int = 5,
    base_url: str = HINDSIGHT_URL,
    bank: str = HINDSIGHT_BANK,
) -> list[TurnMemory]:
    payload = {
        "query": query,
        "types": ["world", "experience"],
        "budget": "low",
        "max_tokens": 2048,
    }
    try:
        code, body = http_json("POST", f"{base_url}/v1/default/banks/{bank}/memories/recall", payload, timeout=15)
    except Exception:
        return []
    if code < 200 or code >= 300:
        return []
    memories = []
    for rank, result in enumerate(body.get("results", [])[:limit], 1):
        text = result.get("text") or result.get("content") or ""
        if not text:
            continue
        memories.append(
            TurnMemory(
                plane="hindsight",
                id=str(result.get("id") or result.get("document_id") or f"hindsight-{rank}"),
                content=text,
                score=1.0 / (60 + rank),
                source="hindsight",
                metadata={
                    "type": result.get("type"),
                    "context": result.get("context"),
                    "entities": result.get("entities", []),
                },
            )
        )
    return memories
