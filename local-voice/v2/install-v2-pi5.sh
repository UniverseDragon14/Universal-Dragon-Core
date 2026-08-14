#!/usr/bin/env bash
set -Eeuo pipefail

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
V1_HOME="${DRAGON_LOCAL_VOICE_HOME:-$HOME/dragon-local-voice-v1}"
V1_ENV="$V1_HOME/.env"
V2_HOME="${DRAGON_LOCAL_VOICE_V2_HOME:-$HOME/dragon-local-voice-v2}"
VENV="$V2_HOME/.venv"
PORT="${DRAGON_LOCAL_VOICE_V2_PORT:-8124}"
SERVICE_DIR="$HOME/.config/systemd/user"
SERVICE_FILE="$SERVICE_DIR/dragon-local-voice-v2.service"
CONFIG_ENV="$V2_HOME/runtime.env"
REFERENCE_DIR="$V2_HOME/references"
CACHE_DIR="$V2_HOME/cache"

printf '%s\n' '=== UNIVERSAL DRAGON HUMAN VOICE SOUL V2 INSTALL ==='

if [ ! -s "$V1_ENV" ]; then
  echo 'V1_SECRET_ENV=MISS'
  exit 4
fi
if ! grep -q '^DRAGON_VOICE_TOKEN=.' "$V1_ENV"; then
  echo 'V1_TOKEN=MISS'
  exit 5
fi
if ! systemctl --user is-active --quiet dragon-local-voice.service; then
  echo 'V1_SERVICE_ACTIVE=NO'
  exit 6
fi
echo 'V1_PROVEN_FALLBACK=PASS'

if ! command -v sudo >/dev/null 2>&1; then
  echo 'SUDO=MISS'
  exit 7
fi

sudo apt-get update
sudo apt-get install -y python3-venv curl ffmpeg espeak-ng libsndfile1
echo 'V2_SYSTEM_DEPENDENCIES=PASS'

mkdir -p "$V2_HOME" "$REFERENCE_DIR" "$CACHE_DIR/huggingface" "$CACHE_DIR/torch" "$SERVICE_DIR"
install -m 0644 "$SOURCE_DIR/dragon_voice_v2_server.py" "$V2_HOME/dragon_voice_v2_server.py"
install -m 0644 "$SOURCE_DIR/voice_soul_v2.py" "$V2_HOME/voice_soul_v2.py"
install -m 0644 "$SOURCE_DIR/profiles-v2.json" "$V2_HOME/profiles-v2.json"
install -m 0644 "$SOURCE_DIR/requirements-v2.txt" "$V2_HOME/requirements-v2.txt"
install -m 0644 "$SOURCE_DIR/requirements-nano.txt" "$V2_HOME/requirements-nano.txt"

test -s "$V2_HOME/dragon_voice_v2_server.py"
test -s "$V2_HOME/profiles-v2.json"
echo 'V2_RUNTIME_FILES=PASS'

python3 -m venv "$VENV"
"$VENV/bin/python" -m pip install --upgrade pip setuptools wheel
"$VENV/bin/python" -m pip install --prefer-binary -r "$V2_HOME/requirements-v2.txt"
"$VENV/bin/python" - <<'PY'
from kokoro import KModel, KPipeline
print("KOKORO_IMPORT=PASS")
PY
echo 'KOKORO_V2_ENV=PASS'

cat >"$CONFIG_ENV" <<EOF
DRAGON_V2_PROFILES=$V2_HOME/profiles-v2.json
DRAGON_V2_REFERENCE_DIR=$REFERENCE_DIR
DRAGON_V1_URL=http://127.0.0.1:8123
DRAGON_VOICE_MAX_TEXT=1200
DRAGON_V2_ALLOW_NANO_WITHOUT_REFERENCE=0
HF_HOME=$CACHE_DIR/huggingface
TORCH_HOME=$CACHE_DIR/torch
XDG_CACHE_HOME=$CACHE_DIR
EOF
chmod 600 "$CONFIG_ENV"
echo 'V2_LOCAL_CONFIG=PASS'

cat >"$SERVICE_FILE" <<EOF
[Unit]
Description=Universal Dragon Human Voice Soul V2
After=network-online.target dragon-local-voice.service
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=$V2_HOME
EnvironmentFile=$V1_ENV
EnvironmentFile=$CONFIG_ENV
ExecStart=$VENV/bin/python -m uvicorn dragon_voice_v2_server:app --app-dir $V2_HOME --host 127.0.0.1 --port $PORT --workers 1
Restart=on-failure
RestartSec=4
TimeoutStopSec=20
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=$V2_HOME

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable --now dragon-local-voice-v2.service
echo 'V2_SERVICE_INSTALL=PASS'

for _ in $(seq 1 45); do
  if curl --silent --fail "http://127.0.0.1:$PORT/health" >"$V2_HOME/health.json"; then
    break
  fi
  sleep 1
done

test -s "$V2_HOME/health.json"
grep -q '"ok":true' "$V2_HOME/health.json"
grep -q '"auth_configured":true' "$V2_HOME/health.json"
grep -q '"kokoro_installed":true' "$V2_HOME/health.json"
grep -q '"paid_api_required":false' "$V2_HOME/health.json"
echo 'HUMAN_VOICE_V2_HEALTH=PASS'

set -a
# shellcheck disable=SC1090
source "$V1_ENV"
set +a

curl --silent --show-error --fail --max-time 60 \
  -H "Authorization: Bearer $DRAGON_VOICE_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"text":"Bro, Human Voice Soul planning is online.","context":"whatsapp","mood":"smile","engine":"auto"}' \
  "http://127.0.0.1:$PORT/v2/plan" \
  -o "$V2_HOME/plan-proof.json"

grep -q '"schema":"dragon.voice-soul.v2"' "$V2_HOME/plan-proof.json"
grep -q '"profile":"whatsapp_natural"' "$V2_HOME/plan-proof.json"
echo 'HUMAN_VOICE_SOUL_V2_PLAN=PASS'

curl --silent --show-error --fail --max-time 900 \
  -D "$V2_HOME/kokoro-proof.headers" \
  -H "Authorization: Bearer $DRAGON_VOICE_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"text":"Universal Dragon Human Voice Soul is online.","profile":"nova_warm","mood":"smile","context":"chat","engine":"kokoro"}' \
  "http://127.0.0.1:$PORT/v2/speak" \
  -o "$V2_HOME/kokoro-proof.wav"

test -s "$V2_HOME/kokoro-proof.wav"
file "$V2_HOME/kokoro-proof.wav" | grep -qi 'wave audio'
grep -qi '^X-Dragon-Voice-Engine: kokoro' "$V2_HOME/kokoro-proof.headers"
grep -qi '^X-Dragon-Paid-API: no' "$V2_HOME/kokoro-proof.headers"
echo 'KOKORO_V2_WAV=PASS'

echo 'NANO_ENGINE_CODE=INCLUDED'
echo 'NANO_RUNTIME_INSTALL=SEPARATE_BOUNDED_STEP'
echo 'PAID_API_USED=NO'
echo 'ELEVENLABS_REQUIRED=NO'
echo 'V3D_TTS_INFERENCE_CLAIMED=NO'
echo "V2_VOICE_API=http://127.0.0.1:$PORT"
echo "V2_PROOF_WAV=$V2_HOME/kokoro-proof.wav"
echo 'DRAGON_HUMAN_VOICE_SOUL_V2=PASS'
