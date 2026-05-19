#!/usr/bin/env bash
# arbiter-push — thin wrapper around push.py
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/push.py" "$@"