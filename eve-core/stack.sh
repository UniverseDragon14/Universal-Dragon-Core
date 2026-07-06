#!/usr/bin/env bash
# eve stack — start/stop the Carry-On daemons (gateway + WhatsApp voice).
# PIDs tracked under $EVE_ROOT/.eve/run so start/stop/status are reliable.

EVE_RUN_DIR="$EVE_ROOT/.eve/run"

_eve_pidfile() { echo "$EVE_RUN_DIR/$1.pid"; }

_eve_alive() {
  local pf; pf="$(_eve_pidfile "$1")"
  [ -f "$pf" ] || return 1
  local pid; pid="$(cat "$pf" 2>/dev/null)"
  [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null
}

_eve_start_one() {
  local name="$1"; shift
  mkdir -p "$EVE_RUN_DIR"
  if _eve_alive "$name"; then eve_info "$name already running (pid $(cat "$(_eve_pidfile "$name")"))"; return 0; fi
  ( cd "$EVE_ROOT" && nohup "$@" >"$EVE_RUN_DIR/$name.log" 2>&1 & echo $! >"$(_eve_pidfile "$name")" )
  sleep 1
  _eve_alive "$name" && eve_ok "$name started (pid $(cat "$(_eve_pidfile "$name")"))" \
    || eve_err "$name failed to start — see $EVE_RUN_DIR/$name.log"
}

_eve_stop_one() {
  local name="$1"
  if _eve_alive "$name"; then
    kill "$(cat "$(_eve_pidfile "$name")")" 2>/dev/null && eve_ok "$name stopped"
  else
    eve_info "$name not running"
  fi
  rm -f "$(_eve_pidfile "$name")"
}

eve_cmd_gateway() {
  case "${1:-start}" in
    start)
      [ -n "${CARRYON_GATEWAY_SECRET:-}${CARRYON_GATEWAY_KEYFILE:-}" ] \
        || eve_die "set CARRYON_GATEWAY_SECRET first (see carryon/.env.example)"
      _eve_start_one gateway "$(eve_python)" -m carryon.carryon_gateway.server ;;
    stop)   _eve_stop_one gateway ;;
    *) eve_err "usage: ./eve gateway [start|stop]"; return 2 ;;
  esac
}

eve_cmd_whatsapp() {
  case "${1:-start}" in
    start)
      _eve_start_one wa-engine "$(eve_python)" -m carryon.whatsapp_voice.engine
      if command -v node >/dev/null && [ -d "$EVE_ROOT/carryon/whatsapp_voice/bridge/node_modules" ]; then
        _eve_start_one wa-bridge node "$EVE_ROOT/carryon/whatsapp_voice/bridge/index.js"
      else
        eve_warn "wa-bridge skipped: run 'npm install' in carryon/whatsapp_voice/bridge first"
      fi ;;
    stop)   _eve_stop_one wa-bridge; _eve_stop_one wa-engine ;;
    *) eve_err "usage: ./eve whatsapp [start|stop]"; return 2 ;;
  esac
}

eve_cmd_status() {
  eve_say "${C_B}EVE · daemon status${C_RESET}"
  for name in gateway wa-engine wa-bridge; do
    if _eve_alive "$name"; then eve_ok "$name  running (pid $(cat "$(_eve_pidfile "$name")"))"
    else eve_info "$name  stopped"; fi
  done
}

eve_cmd_down() {
  _eve_stop_one wa-bridge; _eve_stop_one wa-engine; _eve_stop_one gateway
}

eve_cmd_media() {
  # passthrough to the media pipeline CLI: ./eve media probe in.mp4
  eve_pyrun -m carryon.media_pipeline.cli "$@"
}
