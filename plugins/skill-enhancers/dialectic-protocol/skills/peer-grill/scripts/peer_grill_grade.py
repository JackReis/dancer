#!/usr/bin/env python3
"""peer_grill_grade.py — run verifier/falsifier commands and grade claims.

Usage: peer_grill_grade.py <topic-dir>

Reads every <agent>.claims.yaml in <topic-dir>, executes each claim's
optional `verifier` / `falsifier` blocks, and writes a timestamped grading
table to <topic-dir>/graded.md (append-only).

Per-claim outcome:
  PASS         — verifier present and passed expectation comparator
  FAIL         — verifier present but did not match (or falsifier passed)
  UNVERIFIABLE — no verifier present; cannot be auto-graded
  ERROR        — verifier ran but exited non-zero or timed out

Comparators (all string-prefix-matched on `expect`):
  literal         exact equality of stripped stdout to `expect`
  >N >=N <N <=N   numeric integer compare
  ==N !=N         numeric integer compare
  matches:/RE/    Python re.search on stripped stdout
  contains:STR    substring search
  sha256:HEX      sha256 digest of stdout matches HEX (lower-cased)
  lines:OP        line-count of stdout vs OP (e.g. lines:>200, lines:==15)

If PyYAML is missing, the script falls back to a tiny tolerant parser
sufficient for the schema (same approach as peer_grill_diff.py).

If invoked directly without PyYAML, you can also run via:
    /Users/jack.reis/.mcp-venv/bin/python3 peer_grill_grade.py <dir>
"""
from __future__ import annotations

import datetime
import hashlib
import pathlib
import re
import subprocess
import unicodedata

# Greek-alphabet fingerprint — mirrors peer_grill_fingerprint.py.
# Inlined here so the grader has zero import dependencies on its sibling.
_GREEK_ALPHABET = "αβγδεζηθικλμνξοπρστυφχψω"
_FP_LEN = 4


def fingerprint(claim_id: str) -> str:
    """Deterministic 4-letter Greek fingerprint of a claim id (NFC-normalized)."""
    canonical = unicodedata.normalize("NFC", claim_id).encode("utf-8")
    digest = hashlib.sha256(canonical).digest()
    return "".join(_GREEK_ALPHABET[b % 24] for b in digest[:_FP_LEN])
import sys

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None


# ─── YAML loader (PyYAML if present, else a tiny tolerant fallback) ───
def load_yaml(text: str) -> dict:
    if yaml is not None:
        return yaml.safe_load(text) or {}
    # Minimal fallback: only enough to read agent/claims/verifier shape.
    # If the dump is even mildly exotic, install PyYAML.
    sys.stderr.write(
        "WARN: PyYAML missing; using tolerant fallback parser. "
        "If grading misbehaves, re-run via /Users/jack.reis/.mcp-venv/bin/python3.\n"
    )
    raise SystemExit("PyYAML required for v1 grader")


# ─── Comparator engine ───
def _to_int(s: str) -> int | None:
    try:
        return int(s.strip())
    except (TypeError, ValueError):
        return None


def evaluate(stdout: str, expect: str) -> tuple[bool, str]:
    """Return (passed, explanation). `expect` syntax documented in module docstring."""
    out = stdout.strip()
    e = expect.strip()

    if e.startswith("matches:/") and e.endswith("/"):
        pat = e[len("matches:/"):-1]
        ok = re.search(pat, out) is not None
        return ok, f"regex /{pat}/ {'matched' if ok else 'did NOT match'}"

    if e.startswith("contains:"):
        sub = e[len("contains:"):]
        ok = sub in out
        return ok, f"substring {sub!r} {'found' if ok else 'not found'}"

    if e.startswith("sha256:"):
        want = e[len("sha256:"):].lower()
        got = hashlib.sha256(stdout.encode("utf-8", errors="replace")).hexdigest()
        return got == want, f"sha256: got {got[:12]}…, want {want[:12]}…"

    if e.startswith("lines:"):
        op = e[len("lines:"):]
        actual_lines = len(stdout.splitlines())
        # recurse: re-evaluate the stripped tail against actual_lines as text
        return evaluate(str(actual_lines), op)

    # numeric ops
    for op in (">=", "<=", "==", "!=", ">", "<"):
        if e.startswith(op):
            n = _to_int(e[len(op):])
            actual = _to_int(out)
            if n is None or actual is None:
                return False, f"comparator {op} requires integer; got out={out!r}, expect={e!r}"
            ok = {
                ">": actual > n, ">=": actual >= n,
                "<": actual < n, "<=": actual <= n,
                "==": actual == n, "!=": actual != n,
            }[op]
            return ok, f"{actual} {op} {n}: {'true' if ok else 'false'}"

    # default: literal exact match
    ok = out == e
    return ok, f"literal: {'matched' if ok else f'got {out!r}, want {e!r}'}"


# ─── Command runner ───
def run_check(check: dict) -> tuple[str, str]:
    """Returns (outcome, detail). outcome ∈ {PASS, FAIL, ERROR}."""
    cmd = check.get("cmd", "")
    expect = check.get("expect", "")
    timeout = int(check.get("timeout_seconds", 10))
    if not cmd or not expect:
        return "ERROR", "missing cmd or expect"
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
    except subprocess.TimeoutExpired:
        return "ERROR", f"timeout after {timeout}s"
    except OSError as e:
        return "ERROR", f"OSError: {e}"
    if result.returncode != 0:
        return "ERROR", f"exit={result.returncode}; stderr={result.stderr.strip()[:120]}"
    ok, detail = evaluate(result.stdout, expect)
    return ("PASS" if ok else "FAIL"), detail


# ─── Main ───
def main() -> int:
    if len(sys.argv) != 2:
        sys.stderr.write(__doc__)
        return 2
    topic_dir = pathlib.Path(sys.argv[1]).resolve()
    if not topic_dir.is_dir():
        sys.stderr.write(f"ERR: {topic_dir} is not a directory\n")
        return 2

    claims_files = sorted(topic_dir.glob("*.claims.yaml"))
    if not claims_files:
        sys.stderr.write(f"ERR: no *.claims.yaml in {topic_dir}\n")
        return 1

    rows = []
    for f in claims_files:
        agent = f.name[: -len(".claims.yaml")]
        try:
            data = load_yaml(f.read_text())
        except Exception as e:
            sys.stderr.write(f"WARN: failed to parse {f.name}: {e}\n")
            continue
        for claim in data.get("claims", []):
            cid = claim.get("id", "?")
            ver = claim.get("verifier")
            falsi = claim.get("falsifier")
            if ver:
                outcome, detail = run_check(ver)
                rows.append((agent, cid, "verifier", outcome, detail))
            else:
                rows.append((agent, cid, "verifier", "UNVERIFIABLE", "no verifier field"))
            if falsi:
                outcome, detail = run_check(falsi)
                # For a falsifier: if it PASSES, the claim is FALSIFIED.
                if outcome == "PASS":
                    rows.append((agent, cid, "falsifier", "FALSIFIED", detail))
                elif outcome == "FAIL":
                    rows.append((agent, cid, "falsifier", "PASS", "falsifier did not trigger"))
                else:
                    rows.append((agent, cid, "falsifier", outcome, detail))

    # Tally
    counts: dict[str, int] = {}
    for *_, outcome, _ in rows:
        counts[outcome] = counts.get(outcome, 0) + 1

    # Append to graded.md
    out_path = topic_dir / "graded.md"
    ts = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    lines = [
        f"\n## Grading run — {ts}",
        f"Files graded: {', '.join(f.name for f in claims_files)}",
        "",
        "| ⟦fp⟧ | Agent | Claim | Check | Outcome | Detail |",
        "|---|---|---|---|---|---|",
    ]
    for agent, cid, kind, outcome, detail in rows:
        # escape pipes in detail for markdown
        safe = detail.replace("|", "\\|")
        fp = fingerprint(cid)
        lines.append(f"| ⟦{fp}⟧ | `{agent}` | `{cid}` | {kind} | **{outcome}** | {safe} |")
    lines.append("")
    summary = " · ".join(f"{k}: {v}" for k, v in sorted(counts.items()))
    lines.append(f"**Summary:** {summary}")
    lines.append("")

    with out_path.open("a") as fh:
        fh.write("\n".join(lines))

    sys.stdout.write(f"Graded {len(rows)} checks across {len(claims_files)} agent dump(s).\n")
    sys.stdout.write(f"Summary: {summary}\n")
    sys.stdout.write(f"Appended to: {out_path}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
