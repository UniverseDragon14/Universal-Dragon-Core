#!/data/data/com.termux/files/usr/bin/bash
set -u

LAB="${DRAGON_ROOM_MAGIC_HOME:-$HOME/dragon-room-magic-v1}"
RUN="${DRAGON_ROOM_MAGIC_RUNTIME:-$HOME/.dragon-magic-runtime}"
PORT="${DRAGON_ROOM_MAGIC_PORT:-8765}"
WEB_ROOT="$RUN/www-v3"
URL="http://127.0.0.1:${PORT}/awaken.html"
SOUND="$LAB/dragon-awaken.wav"
VOICE_ADAPTER="$LAB/voice-eleven-v3.sh"
PID_FILE="$RUN/http.pid"
LOG_FILE="$RUN/http.log"
SERVED_COPY="$RUN/served-awaken.html"

mkdir -p "$LAB" "$RUN" "$WEB_ROOT"
chmod 700 "$RUN" "$WEB_ROOT" 2>/dev/null || true

log() {
  printf '%s\n' "$*"
}

best_effort() {
  "$@" >/dev/null 2>&1 || true
}

cleanup() {
  best_effort termux-torch off
  rm -f "$SERVED_COPY" 2>/dev/null || true
}

on_signal() {
  cleanup
  trap - EXIT
  exit 130
}

trap cleanup EXIT
trap on_signal INT TERM

if [ ! -s "$LAB/awaken.html" ]; then
  log "STOP: $LAB/awaken.html missing"
  exit 1
fi

if [ -L "$WEB_ROOT" ]; then
  log "STOP: runtime web root must not be a symlink"
  exit 1
fi

cp "$LAB/awaken.html" "$WEB_ROOT/awaken.html" || exit 1
chmod 600 "$WEB_ROOT/awaken.html" 2>/dev/null || true

is_managed_server() {
  pid="$1"
  [ -n "$pid" ] || return 1
  [ -r "/proc/$pid/cmdline" ] || return 1

  command_line="$(tr '\0' ' ' < "/proc/$pid/cmdline" 2>/dev/null || true)"
  case "$command_line" in
    *"python3 -m http.server $PORT"*"--directory $WEB_ROOT"*) return 0 ;;
    *) return 1 ;;
  esac
}

served_asset_matches() {
  rm -f "$SERVED_COPY" 2>/dev/null || true
  curl -fsS --connect-timeout 2 --max-time 4 "$URL" -o "$SERVED_COPY" 2>/dev/null || return 1
  cmp -s "$WEB_ROOT/awaken.html" "$SERVED_COPY"
}

stop_managed_server() {
  [ -s "$PID_FILE" ] || return 0
  old_pid="$(cat "$PID_FILE" 2>/dev/null || true)"

  if is_managed_server "$old_pid"; then
    kill "$old_pid" 2>/dev/null || true
    for _ in 1 2 3 4 5; do
      kill -0 "$old_pid" 2>/dev/null || break
      sleep 0.1
    done
  fi

  rm -f "$PID_FILE"
}

start_managed_server() {
  stop_managed_server

  python3 -m http.server "$PORT" \
    --bind 127.0.0.1 \
    --directory "$WEB_ROOT" \
    >"$LOG_FILE" 2>&1 &

  server_pid=$!
  printf '%s\n' "$server_pid" > "$PID_FILE"
  sleep 1

  if ! is_managed_server "$server_pid"; then
    log "HTTP_SERVER=FAILED"
    tail -40 "$LOG_FILE" 2>/dev/null || true
    rm -f "$PID_FILE"
    return 1
  fi

  if ! served_asset_matches; then
    log "HTTP_ASSET_IDENTITY=FAIL"
    return 1
  fi

  return 0
}

log "DRAGON_ROOM_MAGIC_V3=START"

if served_asset_matches; then
  log "HTTP_ASSET_IDENTITY=PASS"
else
  if ! start_managed_server; then
    log "VISUAL_HTTP=FAIL"
    exit 1
  fi
  log "HTTP_ASSET_IDENTITY=PASS"
fi

if served_asset_matches; then
  log "VISUAL_HTTP=PASS"
else
  log "VISUAL_HTTP=FAIL"
  exit 1
fi

best_effort termux-open-url "$URL"
best_effort termux-vibrate -d 140
sleep 0.15
best_effort termux-vibrate -d 260

# The generated WAV is a room-effect cue. Spoken voice is a separate layer.
if [ -s "$SOUND" ]; then
  best_effort termux-media-player play "$SOUND"
  log "SOUND_ROLE=ROOM_EFFECT"
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
