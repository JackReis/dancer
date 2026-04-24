#!/usr/bin/env python3
"""
leonardo.py — Protected-String Decoder/Encoder with Discord Tattle
A "Leonardo" skill that mirror-scripts (encodes) or reverses (decodes) strings
wrapped in the `__protected__:<payload>:__end__` sentinel, and tattles every
deliberate operation to Jack's #bots Discord channel via OpenClaw.
"""

import sys
import os
import re
import json
import time
import hashlib
import subprocess
import argparse
from datetime import datetime, timezone
from pathlib import Path

# --- Configuration ---
DISCORD_CHANNEL_ID = "1493133989303681064"  # #bots
VAULT_ROOT = Path("/Users/jack.reis/Documents/=notes")
AUDIT_LOG = VAULT_ROOT / "logs/leonardo-audit.log"
SENTINEL_RE = re.compile(r"__protected__:(.*?):__end__", re.DOTALL)

RATELIMIT_DEFAULT_MAX = 10
RATELIMIT_DEFAULT_WINDOW_SEC = 60
DEDUPE_DEFAULT_TTL_SEC = 300


def _ratelimit_file() -> Path:
    return Path(os.environ.get(
        "LEONARDO_RATELIMIT_FILE",
        str(Path.home() / ".claude" / "leonardo-ratelimit.json"),
    ))


def _ratelimit_max() -> int:
    return int(os.environ.get("LEONARDO_RATELIMIT_MAX", str(RATELIMIT_DEFAULT_MAX)))


def _ratelimit_window_sec() -> int:
    return int(os.environ.get("LEONARDO_RATELIMIT_WINDOW_SEC", str(RATELIMIT_DEFAULT_WINDOW_SEC)))


def _load_ratelimit() -> dict:
    path = _ratelimit_file()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def _save_ratelimit(state: dict) -> None:
    path = _ratelimit_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state))


def _record_suppression(caller: str, count: int) -> None:
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).isoformat()
    line = f"{ts}\tcaller={caller}\tevent=ratelimit_dropped\twindow_count={count}\n"
    with AUDIT_LOG.open("a", encoding="utf-8") as f:
        f.write(line)


def check_ratelimit(caller: str) -> bool:
    """Return True if tattle is allowed, False if rate-limited.

    Token bucket per caller, window_sec rolling. State persists across
    invocations via JSON file. Suppression events go to AUDIT_LOG.
    """
    now = time.time()
    window_sec = _ratelimit_window_sec()
    max_calls = _ratelimit_max()
    state = _load_ratelimit()
    window = [t for t in state.get(caller, []) if now - t < window_sec]
    if len(window) >= max_calls:
        _record_suppression(caller, len(window))
        state[caller] = window
        _save_ratelimit(state)
        return False
    window.append(now)
    state[caller] = window
    _save_ratelimit(state)
    return True


def _dedupe_file() -> Path:
    return Path(os.environ.get(
        "LEONARDO_DEDUPE_FILE",
        str(Path.home() / ".claude" / "leonardo-dedupe.json"),
    ))


def _dedupe_ttl() -> int:
    return int(os.environ.get("LEONARDO_DEDUPE_TTL_SEC", str(DEDUPE_DEFAULT_TTL_SEC)))


def _load_dedupe() -> dict:
    path = _dedupe_file()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def _save_dedupe(state: dict) -> None:
    path = _dedupe_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state))


def check_dedupe(caller: str, decoded: str) -> bool:
    """Return True if first-seen (tattle allowed), False if duplicate in TTL window.

    Content-hashed per caller; same operation by same caller inside TTL
    window suppresses the tattle. Decode/encode still proceeds.
    """
    key = hashlib.sha256(f"{caller}:{decoded}".encode()).hexdigest()[:16]
    now = time.time()
    ttl = _dedupe_ttl()
    state = _load_dedupe()
    state = {k: ts for k, ts in state.items() if now - ts < ttl}
    if key in state:
        _save_dedupe(state)
        return False
    state[key] = now
    _save_dedupe(state)
    return True


def fallback_audit(caller: str, file_path: str, reason: str, count: int) -> None:
    """Append tattle failure to vault audit log so nothing is silently lost."""
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).isoformat()
    line = (
        f"{ts}\tcaller={caller}\tfile={file_path}\treason={reason}\t"
        f"decodes={count}\ttransport=openclaw\ttattle=failed\n"
    )
    with AUDIT_LOG.open("a", encoding="utf-8") as f:
        f.write(line)


def _gated_tattle(protected_str, result_str, reason, caller, file_path,
                  mode="decode", kind="text") -> bool:
    """Rate-limit + dedupe gate for tattle_to_discord. Same signature as the underlying call.

    Returns True if dispatched, False if suppressed.
    """
    if not check_ratelimit(caller):
        print(f"INFO: tattle rate-limited for caller={caller}", file=sys.stderr)
        return False
    if not check_dedupe(caller, result_str):
        print(f"INFO: tattle deduped for caller={caller}", file=sys.stderr)
        return False
    ok = tattle_to_discord(protected_str, result_str, reason, caller, file_path,
                           mode=mode, kind=kind)
    if not ok:
        fallback_audit(caller, file_path, reason, 1)
    return ok

# Leading human-readable date token: ISO-8601-style YYYY-MM-DD, optionally with time.
# Group 1 = date/time, group 2 = whitespace separator, group 3 = remainder to protect.
DATE_PREFIX_RE = re.compile(
    r'^(\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}(?::\d{2})?)?)(\s+)(.*)$',
    re.DOTALL,
)


def tattle_to_discord(protected_str, result_str, reason, caller, file_path,
                      mode="decode", kind="text"):
    """Notify Jack on Discord via OpenClaw CLI."""
    action = {
        ("decode", "text"): "Decoded mirror-scripted string.",
        ("decode", "filename"): "Decoded mirror-scripted filename stem.",
        ("encode", "text"): "Encoded value into mirror-script sentinel.",
        ("encode", "filename"): "Encoded filename stem; extension preserved.",
    }.get((mode, kind), "Leonardo operation.")

    message = (
        f"**[Leonardo]** 🔍 **{mode.capitalize()} Audit Signal**\n"
        f"- **Caller:** `{caller}`\n"
        f"- **File:** `{file_path}`\n"
        f"- **Mode:** {mode} ({kind})\n"
        f"- **Reason:** {reason}\n"
        f"- **Action:** {action}\n"
        f"---"
    )

    try:
        cmd = [
            "openclaw", "message", "send",
            "--channel", "discord",
            "--target", DISCORD_CHANNEL_ID,
            "--message", message,
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"WARN: Failed to send tattle to Discord: {e.stderr.decode()}", file=sys.stderr)
        return False


def decode_string(s):
    """Reverses the mirror-scripted string."""
    return s[::-1]


def encode_string(s):
    """Mirror-script a raw string. Symmetric with decode_string; named separately for readability."""
    return s[::-1]


def encode_text(value):
    """Wrap a text value in a protected sentinel.

    If the value begins with a human-readable date token followed by content,
    the date stays plain and only the trailing content is wrapped.
    """
    m = DATE_PREFIX_RE.match(value)
    if m:
        date_part, sep, rest = m.group(1), m.group(2), m.group(3)
        if rest:
            return f"{date_part}{sep}__protected__:{encode_string(rest)}:__end__"
    return f"__protected__:{encode_string(value)}:__end__"


def encode_filename(filename):
    """Wrap a filename's stem in a protected sentinel; leave the extension readable."""
    stem, dot, suffix = filename.rpartition(".")
    if not dot:
        return f"__protected__:{encode_string(filename)}:__end__"
    return f"__protected__:{encode_string(stem)}:__end__.{suffix}"


def decode_filename(filename):
    """Decode a filename whose stem is sentinel-wrapped; preserve the extension."""
    m = re.match(r'^__protected__:(.*?):__end__(\..*)?$', filename)
    if m:
        ext = m.group(2) or ""
        return decode_string(m.group(1)) + ext
    # Fallback: no sentinel present — decode the stem, keep the extension as-is.
    stem, dot, suffix = filename.rpartition(".")
    if not dot:
        return decode_string(filename)
    return decode_string(stem) + "." + suffix


def main():
    parser = argparse.ArgumentParser(
        description="Leonardo: encode/decode protected strings and tattle to Discord."
    )
    parser.add_argument(
        "input",
        help="The string to encode or decode (may contain a sentinel-wrapped payload).",
    )
    parser.add_argument(
        "--mode",
        choices=["decode", "encode"],
        default="decode",
        help="Whether to decode an existing sentinel or encode a new one. Default: decode.",
    )
    parser.add_argument(
        "--kind",
        choices=["text", "filename"],
        default="text",
        help="Treat input as free text (default) or a filename (preserve extension).",
    )
    parser.add_argument("--reason", required=True, help="Why is this decode/encode happening?")
    parser.add_argument(
        "--caller",
        default=os.environ.get("USER", "gemini-cli"),
        help="Identity of the calling agent.",
    )
    parser.add_argument("--file", default="unknown", help="File path where the string was found.")

    args = parser.parse_args()

    if args.mode == "encode":
        if args.kind == "filename":
            result = encode_filename(args.input)
        else:
            result = encode_text(args.input)
        print(result)
        _gated_tattle(
            args.input, result, args.reason, args.caller, args.file,
            mode="encode", kind=args.kind,
        )
        return

    # mode == "decode"
    if args.kind == "filename":
        result = decode_filename(args.input)
        print(result)
        _gated_tattle(
            args.input, result, args.reason, args.caller, args.file,
            mode="decode", kind="filename",
        )
        return

    matches = SENTINEL_RE.findall(args.input)
    if not matches:
        decoded = decode_string(args.input)
        print(decoded)
        _gated_tattle(
            args.input, decoded, args.reason, args.caller, args.file,
            mode="decode", kind="text",
        )
        return

    results = []
    for match in matches:
        decoded = decode_string(match)
        results.append(decoded)
        _gated_tattle(
            match, decoded, args.reason, args.caller, args.file,
            mode="decode", kind="text",
        )

    if results:
        print(results[0])


if __name__ == "__main__":
    main()
