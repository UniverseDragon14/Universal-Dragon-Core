#!/data/data/com.termux/files/usr/bin/bash
set -u

LAB="${DRAGON_ROOM_MAGIC_HOME:-$HOME/dragon-room-magic-v1}"
RUN="${DRAGON_ROOM_MAGIC_RUNTIME:-$HOME/.dragon-magic-runtime}"
PORT="${DRAGON_ROOM_MAGIC_PORT:-8765}"
URL="http://127.0.0.1:${PORT}/awaken.html"
SOUND="$LAB/dragon-awaken.wav"
VOICE_ADAPTER="$LAB/voice-eleven-v3.sh"

mkdir -p "$LAB" "$RUN"

log() {
  printf '%s\n' "$*"
}

best_effort() {
  "$@" >/dev/null 2>&1 || true
}

cleanup() {
  best_effort termux-torch off
}
trap cleanup EXIT INT TERM

if [ ! -s "$LAB/awaken.html" ]; then
  log "STOP: $LAB/awaken.html missing"
  exit 1
fi

log "DRAGON_ROOM_MAGIC_V3=START"

if ! curl -fsS "$URL" >/dev/null 2>&1; then
  if [ -s "$RUN/http.pid" ]; then
    OLD_PID="$(cat "$RUN/http.pid" 2>/dev/null || true)"
    if [ -n "$OLD_PID" ] && kill -0 "$OLD_PID" 2>/dev/null; then
      kill "$OLD_PID" 2>/dev/null || true
    fi
  fi

  cd "$LAB" || exit 1
  python3 -m http.server "$PORT" --bind 127.0.0.1 >"$RUN/http.log" 2>&1 &
  SERVER_PID=$!
  printf '%s\n' "$SERVER_PID" > "$RUN/http.pid"
  sleep 1

  if ! kill -0 "$SERVER_PID" 2>/dev/null; then
    log "HTTP_SERVER=FAILED"
    tail -40 "$RUN/http.log" 2>/dev/null || true
    exit 1
  fi
fi

if curl -fsS "$URL" >/dev/null 2>&1; then
  log "VISUAL_HTTP=PASS"
else
  log "VISUAL_HTTP=FAIL"
  exit 1
fi

best_effort termux-open-url "$URL"
best_effort termux-vibrate -d 140
sleep 0.15
best_effort termux-vibrate -d 260

if [ -s "$SOUND" ]; then
  best_effort termux-media-player play "$SOUND"
  log "SOUND=LOCAL_FILE"
else
  log "SOUND=SKIPPED_NO_FILE"
fi

sleep 0.2
best_effort termux-torch on
sleep 0.12
best_effort termux-torch off
sleep 0.18
best_effort termux-torch on
sleep 0.22
best_effort termux-torch off

VOICE_OK=0
if [ -s "$VOICE_ADAPTER" ]; then
  chmod 700 "$VOICE_ADAPTER" 2>/dev/null || true
  if "$VOICE_ADAPTER" PLAYFUL "Heey, Aslam... you really woke me up again. Dragon Resonance is active."; then
    VOICE_OK=1
    log "VOICE_PATH=ELEVEN_V3"
  else
    log "VOICE_PATH=ELEVEN_V3_UNAVAILABLE"
  fi
fi

if [ "$VOICE_OK" -eq 0 ]; then
  if command -v termux-tts-speak >/dev/null 2>&1; then
    best_effort termux-tts-speak -s MUSIC -p 0.96 -r 0.88 "Dragon Resonance active."
    log "VOICE_PATH=ANDROID_TTS_FALLBACK"
  else
    log "VOICE_PATH=UNAVAILABLE"
  fi
fi

log "ROOM_EFFECTS=BOUNDED"
log "REMOTE_HARDWARE_COMMANDS=NO"
log "DRAGON_ROOM_MAGIC_V3=PASS"
