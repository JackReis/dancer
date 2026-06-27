"""Honcho plane — the Dialectic API (peer.chat) memory plane.

NEW plane (no SSOT to vendor). Mirrors the Honcho 2.0.1 usage in the reference
client ~/hermes-agent-jr/plugins/memory/honcho/client.py + session.py,
simplified to the Claude Code single-peer case:
  - human peer  = jack.reis
  - assistant   = claude-code
  - session     = claude-code-global  (global session = cross-session continuity)

Named `honcho_plane` (not `honcho`) to avoid shadowing the `honcho` SDK.

The plane's reason to exist: `peer.chat()` (Dialectic API) returns a *synthesis*
of what Honcho knows about jack.reis relevant to the query — not a raw vector
dump. `_get_client` is lazy + lru-cached so plugin import never hard-requires
the SDK or a live container. Every method fails open: an unreachable Honcho
never breaks a turn.
"""

from __future__ import annotations

import os
from functools import lru_cache

from quad_memory.core import PlaneResult, TurnMemory, reject_secret_content


HONCHO_BASE_URL = os.environ.get("HONCHO_BASE_URL", "http://127.0.0.1:8000")
HONCHO_WORKSPACE = os.environ.get("HONCHO_WORKSPACE", "hermes")
HONCHO_HUMAN_PEER = os.environ.get("HONCHO_HUMAN_PEER", "jack.reis")
HONCHO_AI_PEER = os.environ.get("HONCHO_AI_PEER", "claude-code")
HONCHO_SESSION = os.environ.get("HONCHO_SESSION", "claude-code-global")
HONCHO_REASONING = os.environ.get("HONCHO_REASONING_LEVEL", "medium")
MSG_MAX = 25000
DIALECTIC_INPUT_MAX = 10000
DIALECTIC_OUT_MAX = 600


@lru_cache(maxsize=1)
def _get_client():
    from honcho import Honcho  # imported lazily so plugin loads without SDK
    api_key = os.environ.get("HONCHO_API_KEY")  # resolved from ~/.hermes/.env / SOPS / Keychain
    kwargs = {"base_url": HONCHO_BASE_URL, "workspace_id": HONCHO_WORKSPACE}
    if api_key:
        kwargs["api_key"] = api_key
    return Honcho(**kwargs)


def honcho_health() -> PlaneResult:
    try:
        client = _get_client()
        client.peer(HONCHO_AI_PEER)  # cheap construction; deeper probe optional
        return PlaneResult("honcho", True, f"api reachable @ {HONCHO_BASE_URL}")
    except Exception as exc:
        return PlaneResult("honcho", False, f"unreachable: {exc}")


def capture_honcho(content, *, role, source, session_id, **_) -> PlaneResult:
    try:
        reject_secret_content(content)
        client = _get_client()
        peer = client.peer(HONCHO_HUMAN_PEER if role == "user" else HONCHO_AI_PEER)
        session = client.session(HONCHO_SESSION)
        session.add_messages([peer.message(content[:MSG_MAX])])
        return PlaneResult("honcho", True, f"message synced ({role})")
    except Exception as exc:
        return PlaneResult("honcho", False, f"capture failed: {exc}")


def recall_honcho(query, *, limit=1) -> list[TurnMemory]:
    try:
        client = _get_client()
        assistant = client.peer(HONCHO_AI_PEER)
        answer = assistant.chat(query[:DIALECTIC_INPUT_MAX],
                                target=HONCHO_HUMAN_PEER,
                                reasoning_level=HONCHO_REASONING) or ""
        answer = answer[:DIALECTIC_OUT_MAX].strip()
        if not answer:
            return []
        return [TurnMemory(plane="honcho", id="honcho-dialectic-1", content=answer,
                           score=1.0, source="honcho-dialectic", metadata={"kind": "dialectic"})]
    except Exception:
        return []  # fail-open: never break the brief
