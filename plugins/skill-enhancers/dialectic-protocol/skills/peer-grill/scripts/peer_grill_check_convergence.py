#!/usr/bin/env python3
"""peer_grill_check_convergence.py — exit 0 if both agents ratified <claim-id>.

Parses grill-log.md for `RATIFY: <claim-id>` lines, attributing each to the
most recent agent header line. Two header formats are supported:

  Standalone:  [<ISO>] <agent-name>
  Inline:      [<ISO>] <agent-a> -> <agent-b> | claim:<id> | round:N
               [<ISO>] <agent-a> -> <agent-b> | claim:<id> | RATIFY: <id> | ...

If a RATIFY line appears within a standalone-header block, the standalone
agent is credited. If it appears on an inline header line, the asker (left of
->) is credited.

Exit 0 if >= 2 distinct agents ratified the given claim; exit 1 otherwise.
"""
import sys
import pathlib
import re

# Standalone header: "[<ISO>] <agent-name>"  (no pipe, no arrow)
STANDALONE_HEADER = re.compile(r"^\[[^\]]+\]\s+(\S+)\s*$")

# Inline header / inline RATIFY: "[<ISO>] <agent-a> -> <agent-b> | ..."
INLINE_HEADER = re.compile(r"^\[[^\]]+\]\s+(\S+)\s+->\s+\S+\s+\|")


def main(topic_dir, claim_id):
    log_path = pathlib.Path(topic_dir) / "grill-log.md"
    if not log_path.exists():
        print(f"ERROR: {log_path} does not exist", file=sys.stderr)
        return 2

    log = log_path.read_text()
    ratify_marker = f"RATIFY: {claim_id}"

    agents = set()
    current_standalone_agent = None

    for line in log.splitlines():
        # Inline header (with arrow) — also potentially carries RATIFY itself
        m_inline = INLINE_HEADER.match(line)
        if m_inline:
            asker = m_inline.group(1)
            current_standalone_agent = None  # inline header overrides
            if ratify_marker in line:
                agents.add(asker)
            continue

        # Standalone header
        m_standalone = STANDALONE_HEADER.match(line)
        if m_standalone:
            current_standalone_agent = m_standalone.group(1)
            continue

        # RATIFY line attributed to the most recent standalone agent
        if ratify_marker in line and current_standalone_agent:
            agents.add(current_standalone_agent)

    if len(agents) >= 2:
        print(f"CONVERGED: {claim_id} ratified by {sorted(agents)}")
        return 0
    print(f"NOT-YET: {claim_id} ratified by only {sorted(agents)}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(
            "Usage: peer_grill_check_convergence.py <topic-dir> <claim-id>",
            file=sys.stderr,
        )
        sys.exit(2)
    sys.exit(main(sys.argv[1], sys.argv[2]))
