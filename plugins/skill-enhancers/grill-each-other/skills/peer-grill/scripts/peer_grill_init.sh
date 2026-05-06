#!/usr/bin/env bash
# peer_grill_init.sh — bootstrap a peer-grill working dir
# Usage: peer_grill_init.sh <topic> <agent-name>
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <topic> <agent-name>" >&2
  exit 2
fi

TOPIC="$1"
AGENT="$2"
DIR=".peer-grill/${TOPIC}"

mkdir -p "$DIR"

CLAIMS="${DIR}/${AGENT}.claims.yaml"
if [[ -f "$CLAIMS" ]]; then
  echo "Refusing to overwrite existing $CLAIMS" >&2
  exit 3
fi

cat > "$CLAIMS" <<EOF
agent: ${AGENT}
session_started: $(date -u +%Y-%m-%dT%H:%M:%SZ)
scope: [infra, code, decision, open-work]
claims: []
# Fill in claims as: id, statement, confidence (high|medium|low), source, scope, last_verified
EOF

# Touch the append-only files so other agent's diff doesn't 404
touch "${DIR}/grill-log.md" "${DIR}/diff.md" "${DIR}/unresolved.md" "${DIR}/signoff.md"

echo "Initialized peer-grill at ${DIR} for agent ${AGENT}"
echo "Next: edit ${CLAIMS} with your independent state dump."
