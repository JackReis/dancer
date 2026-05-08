#!/usr/bin/env python3
"""peer_grill_diff.py — compute three-bucket diff from two claims.yaml files.

Usage: peer_grill_diff.py <topic-dir>

Appends a timestamped block to <topic-dir>/diff.md with three sections:
- AGREED:    same id, same statement
- DISAGREED: same id, different statements
- ONLY <agent>: id present in only one agent's file

Also performs stdlib structural validation against schemas/claims.schema.json
(required fields, confidence enum, scope enum, id pattern). Violations are
printed to stderr but do NOT block the diff — the protocol prefers continuing
with a warning over hiding bad data.

Dependency: PyYAML. Install via `pip install pyyaml` or run from a venv that
has it. The skill ships a stdlib-only convergence checker, signoff tool, and
fingerprint tool; only diff.py and grade.py require PyYAML.
"""
import datetime
import pathlib
import re
import sys

try:
    import yaml  # PyYAML
except ImportError:
    sys.stderr.write(
        "ERROR: peer_grill_diff.py requires PyYAML.\n"
        "  Install: pip install pyyaml\n"
        "  Or run from a Python that has it (e.g., a venv).\n"
    )
    sys.exit(2)

VALID_CONFIDENCE = {"high", "medium", "low"}
VALID_SCOPES = {"infra", "code", "decision", "open-work"}
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_.-]*$")
REQUIRED_TOP = {"agent", "session_started", "scope", "claims"}
REQUIRED_CLAIM = {"id", "statement", "confidence", "source", "scope"}


def parse_yaml(text):
    return yaml.safe_load(text)


def validate(data, fname):
    """Stdlib structural check. Print warnings, don't raise."""
    out = []

    def warn(msg):
        out.append(f"{fname}: {msg}")

    if not isinstance(data, dict):
        warn("top-level is not a mapping")
        return out
    missing = REQUIRED_TOP - set(data)
    if missing:
        warn(f"missing top-level fields: {sorted(missing)}")
    declared_scopes = set(data.get("scope") or [])
    bad_top = declared_scopes - VALID_SCOPES
    if bad_top:
        warn(f"scope has unknown values: {sorted(bad_top)}")
    for i, claim in enumerate(data.get("claims") or []):
        if not isinstance(claim, dict):
            warn(f"claim #{i} is not a mapping")
            continue
        cid = claim.get("id", "?")
        miss = REQUIRED_CLAIM - set(claim)
        if miss:
            warn(f"claim {cid!r}: missing {sorted(miss)}")
        if cid != "?" and not ID_PATTERN.match(cid):
            warn(f"claim id {cid!r}: bad pattern")
        conf = claim.get("confidence")
        if conf and conf not in VALID_CONFIDENCE:
            warn(f"claim {cid!r}: bad confidence {conf!r}")
        sc = claim.get("scope")
        if sc and sc not in VALID_SCOPES:
            warn(f"claim {cid!r}: bad scope {sc!r}")
    return out


def main(topic_dir):
    topic = pathlib.Path(topic_dir)
    claim_files = sorted(topic.glob("*.claims.yaml"))
    if len(claim_files) != 2:
        print(
            f"ERROR: expected exactly 2 *.claims.yaml files, found {len(claim_files)}",
            file=sys.stderr,
        )
        sys.exit(2)

    a_path, b_path = claim_files
    a = parse_yaml(a_path.read_text())
    b = parse_yaml(b_path.read_text())

    all_warnings = validate(a, a_path.name) + validate(b, b_path.name)
    if all_warnings:
        sys.stderr.write("Schema warnings (diff continues):\n")
        for w in all_warnings:
            sys.stderr.write(f"  - {w}\n")

    a_name = a.get("agent", a_path.stem.replace(".claims", ""))
    b_name = b.get("agent", b_path.stem.replace(".claims", ""))

    a_claims = {c["id"]: c for c in (a.get("claims") or []) if "id" in c}
    b_claims = {c["id"]: c for c in (b.get("claims") or []) if "id" in c}

    agreed, disagreed, only_a, only_b = [], [], [], []
    for cid in sorted(set(a_claims) | set(b_claims)):
        if cid in a_claims and cid in b_claims:
            sa = " ".join(a_claims[cid]["statement"].split())
            sb = " ".join(b_claims[cid]["statement"].split())
            if sa == sb:
                agreed.append((cid, sa))
            else:
                disagreed.append((cid, sa, sb))
        elif cid in a_claims:
            only_a.append((cid, a_claims[cid]["statement"]))
        else:
            only_b.append((cid, b_claims[cid]["statement"]))

    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    out = [f"\n## Diff computed {ts} (by tooling, peers: {a_name}, {b_name})\n"]
    if all_warnings:
        out.append("### Schema warnings\n")
        out += [f"- {w}" for w in all_warnings]
        out.append("")
    out.append("### AGREED\n")
    out += [f"- `{cid}`: {s}" for cid, s in agreed] or ["- (none)"]
    out.append("\n### DISAGREED\n")
    out += [
        f"- `{cid}`:\n  - {a_name}: {sa}\n  - {b_name}: {sb}"
        for cid, sa, sb in disagreed
    ] or ["- (none)"]
    out.append(f"\n### ONLY {a_name}\n")
    out += [f"- `{cid}`: {s}" for cid, s in only_a] or ["- (none)"]
    out.append(f"\n### ONLY {b_name}\n")
    out += [f"- `{cid}`: {s}" for cid, s in only_b] or ["- (none)"]

    diff_path = topic / "diff.md"
    with diff_path.open("a") as f:
        f.write("\n".join(out) + "\n")

    print(
        f"Wrote diff to {diff_path} ({len(agreed)} agreed, "
        f"{len(disagreed)} disagreed, {len(only_a)+len(only_b)} only-one"
        + (f", {len(all_warnings)} warning(s)" if all_warnings else "")
        + ")"
    )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: peer_grill_diff.py <topic-dir>", file=sys.stderr)
        sys.exit(2)
    main(sys.argv[1])
