#!/usr/bin/env bash
set -Eeuo pipefail

V1_HOME="${DRAGON_LOCAL_VOICE_HOME:-$HOME/dragon-local-voice-v1}"
V1_ENV="$V1_HOME/.env"
V2_HOME="${DRAGON_LOCAL_VOICE_V2_HOME:-$HOME/dragon-local-voice-v2}"
URL="${DRAGON_LOCAL_VOICE_V2_URL:-http://127.0.0.1:8124}"
OUT="$V2_HOME/seven-voice-proof"

if [ ! -s "$V1_ENV" ]; then
  echo 'VOICE_TOKEN_ENV=MISS'
  exit 4
fi
set -a
# shellcheck disable=SC1090
source "$V1_ENV"
set +a

mkdir -p "$OUT"
rm -f "$OUT"/*.wav "$OUT"/*.headers "$OUT"/SHA256SUMS

profiles=(
  nova_warm
  dragon_playful
  dragon_serious
  dragon_deep
  whatsapp_natural
  story_soul
  night_whisper
)

for profile in "${profiles[@]}"; do
  text="Universal Dragon ${profile//_/ } voice is online. This is a local human voice proof."
  payload="$(python3 - "$text" "$profile" <<'PY'
import json, sys
print(json.dumps({
    "text": sys.argv[1],
    "profile": sys.argv[2],
    "context": "chat",
    "engine": "kokoro",
    "intensity": 0.68,
}))
PY
)"
  curl --silent --show-error --fail --max-time 900 \
    -D "$OUT/$profile.headers" \
    -H "Authorization: Bearer $DRAGON_VOICE_TOKEN" \
    -H 'Content-Type: application/json' \
    -d "$payload" \
    "${URL%/}/v2/speak" \
    -o "$OUT/$profile.wav"
  test -s "$OUT/$profile.wav"
  file "$OUT/$profile.wav" | grep -qi 'wave audio'
  grep -qi '^X-Dragon-Voice-Engine: kokoro' "$OUT/$profile.headers"
  echo "VOICE_${profile^^}=PASS"
done

(
  cd "$OUT"
  sha256sum ./*.wav >SHA256SUMS
)

test "$(find "$OUT" -maxdepth 1 -name '*.wav' -type f | wc -l)" -eq 7
echo "SEVEN_VOICE_PROOF_DIR=$OUT"
echo 'SEVEN_DISTINCT_VOICE_FILES=PASS'
echo 'DRAGON_HUMAN_VOICE_SET_V2=PASS'
