#!/usr/bin/env bash
set -Eeuo pipefail

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_HOME="${DRAGON_LOCAL_VOICE_HOME:-$HOME/dragon-local-voice-v1}"
MODEL_DIR="$APP_HOME/models"
VENV="$APP_HOME/.venv"
PORT="${DRAGON_LOCAL_VOICE_PORT:-8123}"
BOOTSTRAP_VOICE="en_US-lessac-medium"
SERVICE_DIR="$HOME/.config/systemd/user"
SERVICE_FILE="$SERVICE_DIR/dragon-local-voice.service"
ENV_FILE="$APP_HOME/.env"

printf '%s\n' '=== UNIVERSAL DRAGON LOCAL VOICE V1 INSTALL ==='

if ! command -v python3 >/dev/null 2>&1; then
  echo 'PYTHON3=MISS'
  exit 4
fi

if command -v sudo >/dev/null 2>&1; then
  sudo apt-get update
  sudo apt-get install -y python3-venv curl ffmpeg
else
  echo 'SUDO=MISS'
  exit 5
fi

echo 'SYSTEM_DEPENDENCIES=PASS'

mkdir -p "$APP_HOME" "$MODEL_DIR" "$SERVICE_DIR"
install -m 0644 "$SOURCE_DIR/dragon_voice_server.py" "$APP_HOME/dragon_voice_server.py"
install -m 0644 "$SOURCE_DIR/profiles.json" "$APP_HOME/profiles.json"
install -m 0644 "$SOURCE_DIR/requirements.txt" "$APP_HOME/requirements.txt"

python3 -m venv "$VENV"
"$VENV/bin/python" -m pip install --upgrade pip setuptools wheel
"$VENV/bin/python" -m pip install -r "$APP_HOME/requirements.txt"
echo 'PYTHON_ENV=PASS'

if [ ! -s "$MODEL_DIR/${BOOTSTRAP_VOICE}.onnx" ]; then
  (
    cd "$MODEL_DIR"
    "$VENV/bin/python" -m piper.download_voices "$BOOTSTRAP_VOICE"
  )
fi

test -s "$MODEL_DIR/${BOOTSTRAP_VOICE}.onnx"
test -s "$MODEL_DIR/${BOOTSTRAP_VOICE}.onnx.json"
echo "BOOTSTRAP_MODEL=$BOOTSTRAP_VOICE"
echo 'BOOTSTRAP_MODEL=PASS'

if [ ! -s "$ENV_FILE" ]; then
  TOKEN="$("$VENV/bin/python" - <<'PY'
import secrets
print(secrets.token_urlsafe(48))
PY
)"
  umask 077
  cat >"$ENV_FILE" <<EOF
DRAGON_VOICE_TOKEN=$TOKEN
DRAGON_VOICE_MODEL_DIR=$MODEL_DIR
DRAGON_VOICE_PROFILES=$APP_HOME/profiles.json
DRAGON_VOICE_MAX_TEXT=1200
EOF
fi
chmod 600 "$ENV_FILE"
grep -q '^DRAGON_VOICE_TOKEN=.' "$ENV_FILE"
echo 'LOCAL_SECRET_FILE=PASS'

cat >"$SERVICE_FILE" <<EOF
[Unit]
Description=Universal Dragon Local Voice V1
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=$APP_HOME
EnvironmentFile=$ENV_FILE
ExecStart=$VENV/bin/python -m uvicorn dragon_voice_server:app --app-dir $APP_HOME --host 127.0.0.1 --port $PORT --workers 1
Restart=on-failure
RestartSec=3
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=$APP_HOME

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable --now dragon-local-voice.service

echo 'SERVICE_INSTALL=PASS'

for _ in $(seq 1 30); do
  if curl --silent --fail "http://127.0.0.1:$PORT/health" >"$APP_HOME/health.json"; then
    break
  fi
  sleep 1
done

grep -q '"ok":true' "$APP_HOME/health.json"
grep -q '"paid_api_required":false' "$APP_HOME/health.json"
grep -q '"auth_configured":true' "$APP_HOME/health.json"
echo 'LOCAL_VOICE_HEALTH=PASS'

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

curl --silent --show-error --fail \
  -H "Authorization: Bearer $DRAGON_VOICE_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"text":"Universal Dragon local voice is online.","profile":"nova_warm","intensity":0.65}' \
  "http://127.0.0.1:$PORT/v1/speak" \
  -o "$APP_HOME/proof.wav"

test -s "$APP_HOME/proof.wav"
file "$APP_HOME/proof.wav" | grep -qi 'wave audio'
echo 'LOCAL_WAV_GENERATION=PASS'

echo 'PAID_API_USED=NO'
echo 'ELEVENLABS_REQUIRED=NO'
echo 'V3D_TTS_INFERENCE_CLAIMED=NO'
echo "VOICE_API=http://127.0.0.1:$PORT"
echo "PROOF_WAV=$APP_HOME/proof.wav"
echo 'DRAGON_LOCAL_VOICE_V1=PASS'
