#!/usr/bin/env bash
# Launch the Carry-On command gateway. Run from repo root:
#   ./carryon/scripts/run_gateway.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

[ -f .env ] && set -a && . ./.env && set +a || true

if [ -z "${CARRYON_GATEWAY_SECRET:-}" ] && [ -z "${CARRYON_GATEWAY_KEYFILE:-}" ]; then
  echo "[carryon] ERROR: set CARRYON_GATEWAY_SECRET or CARRYON_GATEWAY_KEYFILE first." >&2
  exit 1
fi

exec python -m carryon.carryon_gateway.server
