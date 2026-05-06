#!/usr/bin/env python3
# When invoked directly (./peer_grill_diff.py), system python3 is used.
# If PyYAML is not installed, the script will tell you. Recommended:
# invoke as `/Users/jack.reis/.mcp-venv/bin/python3 peer_grill_diff.py <dir>`
# or any python with PyYAML available.
"""peer_grill_diff.py — compute three-bucket diff from two claims.yaml files.

Usage: peer_grill_diff.py <topic-dir>

Appends a timestamped block to <topic-dir>/diff.md with three sections:
- AGREED:    same id, same statement
- DISAGREED: same id, different statements
- ONLY <agent>: id present in only one agent's file
"""
import sys
import pathlib
import datetime

try:
    import yaml  # PyYAML if available
except ImportError:
    yaml = None


def parse_yaml(text):
    if yaml:
        return yaml.safe_load(text)
    raise SystemExit("PyYAML required: pip install pyyaml")


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
    a_name = a.get("agent", a_path.stem.replace(".claims", ""))
    b_name = b.get("agent", b_path.stem.replace(".claims", ""))

    a_claims = {c["id"]: c for c in (a.get("claims") or [])}
    b_claims = {c["id"]: c for c in (b.get("claims") or [])}

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
        f"{len(disagreed)} disagreed, {len(only_a)+len(only_b)} only-one)"
    )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: peer_grill_diff.py <topic-dir>", file=sys.stderr)
        sys.exit(2)
    main(sys.argv[1])
