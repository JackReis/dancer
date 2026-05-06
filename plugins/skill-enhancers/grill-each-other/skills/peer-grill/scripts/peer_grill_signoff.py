#!/usr/bin/env python3
"""peer_grill_signoff.py — compute sha256 of state.merged.yaml, append signoff line.

Usage: peer_grill_signoff.py <topic-dir> <agent-name>
"""
import sys
import pathlib
import hashlib
import datetime


def main(topic_dir, agent_name):
    topic = pathlib.Path(topic_dir)
    merged = topic / "state.merged.yaml"
    if not merged.exists():
        print(
            f"ERROR: {merged} does not exist - cannot sign off",
            file=sys.stderr,
        )
        return 2
    sha = hashlib.sha256(merged.read_bytes()).hexdigest()
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    block = (
        f"\n---\nagent: {agent_name}\n"
        f"timestamp: {ts}\n"
        f"merged_state_sha256: {sha}\n"
        f'attestation: "I attest the above merged state as the agreed truth as of this timestamp."\n'
    )
    with (topic / "signoff.md").open("a") as f:
        f.write(block)
    print(f"Signed off as {agent_name}: sha256={sha}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(
            "Usage: peer_grill_signoff.py <topic-dir> <agent-name>",
            file=sys.stderr,
        )
        sys.exit(2)
    sys.exit(main(sys.argv[1], sys.argv[2]))
