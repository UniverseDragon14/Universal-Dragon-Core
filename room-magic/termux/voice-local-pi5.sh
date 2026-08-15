#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

VOICE_URL="${DRAGON_LOCAL_VOICE_URL:-}"
TOKEN="${DRAGON_LOCAL_VOICE_TOKEN:-}"
PROFILE="${DRAGON_LOCAL_VOICE_PROFILE:-whatsapp_natural}"
TEXT="${*:-}"
OUT="${DRAGON_LOCAL_VOICE_OUT:-$HOME/dragon-voice-reply.wav}"
MAX_TEXT=1200

if [ -z "$VOICE_URL" ]; then
  echo 'DRAGON_LOCAL_VOICE_URL=MISS'
  exit 2
fi
if [ -z "$TOKEN" ]; then
  echo 'DRAGON_LOCAL_VOICE_TOKEN=MISS'
  exit 3
fi
if [ -z "$TEXT" ]; then
  echo 'usage: voice-local-pi5.sh "text to speak"'
  exit 4
fi
if [ "${#TEXT}" -gt "$MAX_TEXT" ]; then
  echo "VOICE_TEXT_TOO_LONG=${#TEXT}"
  echo "VOICE_TEXT_MAX=$MAX_TEXT"
  exit 5
fi

PAYLOAD="$(python - "$TEXT" "$PROFILE" <<'PY'
import json, sys
print(json.dumps({"text": sys.argv[1], "profile": sys.argv[2], "intensity": 0.65}))
PY
)"

curl --silent --show-error --fail \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d "$PAYLOAD" \
  "${VOICE_URL%/}/v1/speak" \
  -o "$OUT"

test -s "$OUT"
echo "VOICE_FILE=$OUT"
echo "VOICE_PROFILE=$PROFILE"
echo 'LOCAL_PI5_VOICE_FETCH=PASS'

if command -v termux-media-player >/dev/null 2>&1; then
  termux-media-player play "$OUT" >/dev/null 2>&1 || true
fi
