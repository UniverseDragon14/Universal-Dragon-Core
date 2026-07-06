#!/usr/bin/env bash
# Example independent sub-agent launched via the gateway.
set -euo pipefail
echo "[subagent:example] started pid=$$" >&2
# exec node ../../server.ts   # or python -m your.agent, etc.
sleep 1
