#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

VOICE_URL="${DRAGON_LOCAL_VOICE_V2_URL:-}"
TOKEN="${DRAGON_LOCAL_VOICE_TOKEN:-}"
PROFILE="${DRAGON_LOCAL_VOICE_PROFILE:-whatsapp_natural}"
MOOD="${DRAGON_LOCAL_VOICE_MOOD:-neutral}"
CONTEXT="${DRAGON_LOCAL_VOICE_CONTEXT:-whatsapp}"
REACTION="${DRAGON_LOCAL_VOICE_REACTION:-none}"
ENGINE="${DRAGON_LOCAL_VOICE_ENGINE:-auto}"
TEXT="${*:-}"
OUT="${DRAGON_LOCAL_VOICE_OUT:-$HOME/dragon-voice-reply-v2.wav}"
MAX_TEXT=1200

if [ -z "$VOICE_URL" ]; then
  echo 'DRAGON_LOCAL_VOICE_V2_URL=MISS'
  exit 2
fi
if [ -z "$TOKEN" ]; then
  echo 'DRAGON_LOCAL_VOICE_TOKEN=MISS'
  exit 3
fi
if [ -z "$TEXT" ]; then
  echo 'usage: voice-local-pi5-v2.sh "text to speak"'
  exit 4
fi
if [ "${#TEXT}" -gt "$MAX_TEXT" ]; then
  echo "VOICE_TEXT_TOO_LONG=${#TEXT}"
  echo "VOICE_TEXT_MAX=$MAX_TEXT"
  exit 5
fi

PAYLOAD="$(python - "$TEXT" "$PROFILE" "$MOOD" "$CONTEXT" "$REACTION" "$ENGINE" <<'PY'
import json, sys
print(json.dumps({
    "text": sys.argv[1],
    "profile": sys.argv[2],
    "mood": sys.argv[3],
    "context": sys.argv[4],
    "reaction": sys.argv[5],
    "engine": sys.argv[6],
    "intensity": 0.68,
}))
PY
)"

HEADERS="${OUT}.headers"
curl --silent --show-error --fail --max-time 900 \
  -D "$HEADERS" \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d "$PAYLOAD" \
  "${VOICE_URL%/}/v2/speak" \
  -o "$OUT"

test -s "$OUT"
echo "VOICE_FILE=$OUT"
echo "VOICE_PROFILE=$PROFILE"
echo "VOICE_MOOD=$MOOD"
echo "VOICE_CONTEXT=$CONTEXT"
awk -F': ' 'BEGIN{IGNORECASE=1} /^X-Dragon-Voice-Engine:/{gsub(/\r/,"",$2); print "VOICE_ENGINE=" $2}' "$HEADERS"
echo 'LOCAL_PI5_HUMAN_VOICE_V2_FETCH=PASS'

if command -v termux-media-player >/dev/null 2>&1; then
  termux-media-player play "$OUT" >/dev/null 2>&1 || true
fi
