#!/data/data/com.termux/files/usr/bin/bash
set -u

SECRET_FILE="${ELEVENLABS_SECRET_FILE:-$HOME/.config/universal-dragon/secrets/elevenlabs.env}"
RUN="${DRAGON_ROOM_MAGIC_RUNTIME:-$HOME/.dragon-magic-runtime}"
MOOD="${1:-PLAYFUL}"
shift || true
TEXT="${*:-Heey, Aslam... Dragon Resonance is active.}"
OUT="$RUN/dragon-voice-eleven-v3.mp3"
TMP="$OUT.tmp"

mkdir -p "$RUN"
chmod 700 "$RUN" 2>/dev/null || true

if [ ! -r "$SECRET_FILE" ]; then
  echo "VOICE_PROVIDER=ELEVENLABS"
  echo "VOICE_CONFIG=NOT_FOUND"
  exit 20
fi

set -a
# shellcheck disable=SC1090
source "$SECRET_FILE"
set +a

: "${ELEVENLABS_API_KEY:=}"
: "${ELEVENLABS_VOICE_ID:=}"
: "${ELEVENLABS_MODEL:=eleven_v3}"

if [ -z "$ELEVENLABS_API_KEY" ] || [ -z "$ELEVENLABS_VOICE_ID" ]; then
  echo "VOICE_PROVIDER=ELEVENLABS"
  echo "VOICE_CONFIG=INCOMPLETE"
  exit 21
fi

case "${MOOD^^}" in
  PLAYFUL)
    PREFIX='[mischievously] [laughs softly]'
    ;;
  CURIOUS)
    PREFIX='[curious]'
    ;;
  SERIOUS)
    PREFIX='[firmly] [clears throat]'
    ;;
  WHISPER)
    PREFIX='[whispers]'
    ;;
  CALM|*)
    PREFIX='[warmly]'
    ;;
esac

PROVIDER_TEXT="$PREFIX $TEXT"
PAYLOAD="$({ PROVIDER_TEXT="$PROVIDER_TEXT" ELEVENLABS_MODEL="$ELEVENLABS_MODEL" python3 - <<'PY'
import json
import os

print(json.dumps({
    "text": os.environ["PROVIDER_TEXT"],
    "model_id": os.environ["ELEVENLABS_MODEL"],
}, ensure_ascii=False))
PY
} 2>/dev/null)"

if [ -z "$PAYLOAD" ]; then
  echo "VOICE_PAYLOAD=FAIL"
  exit 22
fi

rm -f "$TMP"
HTTP_CODE="$({
  curl -sS \
    --connect-timeout 10 \
    --max-time 60 \
    -o "$TMP" \
    -w '%{http_code}' \
    -X POST \
    "https://api.elevenlabs.io/v1/text-to-speech/${ELEVENLABS_VOICE_ID}?output_format=mp3_44100_128" \
    -H "xi-api-key: $ELEVENLABS_API_KEY" \
    -H 'Content-Type: application/json' \
    -H 'Accept: audio/mpeg' \
    --data-binary "$PAYLOAD"
} 2>/dev/null || true)"

if [ "$HTTP_CODE" != "200" ]; then
  rm -f "$TMP"
  echo "VOICE_PROVIDER=ELEVENLABS"
  echo "VOICE_HTTP=${HTTP_CODE:-000}"
  echo "VOICE_GENERATION=FAIL"
  exit 23
fi

BYTES="$(wc -c < "$TMP" 2>/dev/null || printf 0)"
if [ "$BYTES" -lt 1000 ]; then
  rm -f "$TMP"
  echo "VOICE_AUDIO_BYTES=$BYTES"
  echo "VOICE_GENERATION=INVALID_AUDIO"
  exit 24
fi

mv "$TMP" "$OUT"
chmod 600 "$OUT" 2>/dev/null || true

if command -v termux-media-player >/dev/null 2>&1; then
  termux-media-player play "$OUT" >/dev/null 2>&1 || true
fi

printf 'VOICE_PROVIDER=ELEVENLABS\n'
printf 'VOICE_MODEL=%s\n' "$ELEVENLABS_MODEL"
printf 'VOICE_MOOD=%s\n' "${MOOD^^}"
printf 'VOICE_AUDIO_BYTES=%s\n' "$BYTES"
printf 'VOICE_SECRET_EXPOSED=NO\n'
printf 'DRAGON_VOICE_ELEVEN_V3=PASS\n'
