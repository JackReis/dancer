#!/usr/bin/env bash
# tests/test_init.sh — verify peer_grill_init.sh creates expected structure
set -euo pipefail
TMPDIR=$(mktemp -d)
cd "$TMPDIR"
bash ~/.claude/skills/peer-grill/scripts/peer_grill_init.sh test-topic claude-laptop
test -d ".peer-grill/test-topic" || { echo "FAIL: dir not created"; exit 1; }
test -f ".peer-grill/test-topic/claude-laptop.claims.yaml" || { echo "FAIL: claims file not created"; exit 1; }
grep -q "agent: claude-laptop" ".peer-grill/test-topic/claude-laptop.claims.yaml" || { echo "FAIL: agent name not stamped"; exit 1; }
test -f ".peer-grill/test-topic/grill-log.md" || { echo "FAIL: grill-log.md not touched"; exit 1; }
test -f ".peer-grill/test-topic/diff.md" || { echo "FAIL: diff.md not touched"; exit 1; }
test -f ".peer-grill/test-topic/unresolved.md" || { echo "FAIL: unresolved.md not touched"; exit 1; }
test -f ".peer-grill/test-topic/signoff.md" || { echo "FAIL: signoff.md not touched"; exit 1; }
echo "PASS"
rm -rf "$TMPDIR"
