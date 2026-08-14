#!/usr/bin/env bash
set -Eeuo pipefail

V2_HOME="${DRAGON_LOCAL_VOICE_V2_HOME:-$HOME/dragon-local-voice-v2}"
VENV="$V2_HOME/.venv"
REQ="$V2_HOME/requirements-nano.txt"

printf '%s\n' '=== UNIVERSAL DRAGON CHATTERBOX NANO INSTALL ==='

if [ ! -x "$VENV/bin/python" ] || [ ! -s "$REQ" ]; then
  echo 'HUMAN_VOICE_V2_BASE=MISS'
  exit 4
fi

"$VENV/bin/python" -m pip install --prefer-binary -r "$REQ"
"$VENV/bin/python" - <<'PY'
from chatterbox.tts_turbo import ChatterboxTurboTTS
print("CHATTERBOX_NANO_IMPORT=PASS")
PY

systemctl --user restart dragon-local-voice-v2.service
for _ in $(seq 1 45); do
  if curl --silent --fail http://127.0.0.1:8124/health >"$V2_HOME/nano-health.json"; then
    break
  fi
  sleep 1
done

grep -q '"nano_installed":true' "$V2_HOME/nano-health.json"
echo 'CHATTERBOX_NANO_INSTALL=PASS'
echo 'NANO_REFERENCE_POLICY=LOCAL_PERMISSIONED_WAV_ONLY'
echo 'NANO_AUDIO_PROOF=REQUIRES_REFERENCE_OR_EXPLICIT_TEST_MODE'
echo 'PAID_API_USED=NO'
echo 'V3D_TTS_INFERENCE_CLAIMED=NO'
