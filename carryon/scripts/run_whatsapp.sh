#!/usr/bin/env bash
# Launch the WhatsApp voice stack: Node bridge (WhatsApp socket) + Python engine.
# Both log to stderr. Run from the repo root: ./carryon/scripts/run_whatsapp.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

[ -f .env ] && set -a && . ./.env && set +a || true

echo "[carryon] starting Python voice engine..." >&2
python -m carryon.whatsapp_voice.engine &
ENGINE_PID=$!

echo "[carryon] starting Node WhatsApp bridge..." >&2
( cd carryon/whatsapp_voice/bridge && node index.js ) &
BRIDGE_PID=$!

trap 'kill "$ENGINE_PID" "$BRIDGE_PID" 2>/dev/null || true' INT TERM
wait
