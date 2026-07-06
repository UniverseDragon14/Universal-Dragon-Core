#!/usr/bin/env bash
# eve mythos — the grand awakening. Boots the whole Universal Dragon world.
#
#   ./eve mythos          -> awaken & map the world (safe, launches nothing)
#   ./eve mythos --boot   -> awaken AND start the live daemons (gateway + voice)

_eve_beat() { printf '%s' "$*" >&2; sleep "${EVE_MYTHOS_DELAY:-0.35}"; printf '\n' >&2; }

_eve_probe() {
  # $1 label, then a command to test presence. Safe under `set -e` because the
  # command is evaluated as an `if` condition, so a missing subsystem just reads
  # as "dormant" instead of aborting the awakening.
  local label="$1"; shift
  if "$@" >/dev/null 2>&1; then
    _eve_beat "  ${C_GRN}✦${C_RESET} $label ${C_DIM}… online${C_RESET}"
  else
    _eve_beat "  ${C_YEL}◦${C_RESET} $label ${C_DIM}… dormant${C_RESET}"
  fi
}

eve_cmd_mythos() {
  local boot=0
  [ "${1:-}" = "--boot" ] && boot=1

  eve_banner
  eve_dragon
  eve_say "${C_B}${C_MAG}  ⟪  M Y T H O S   A W A K E N I N G  ⟫${C_RESET}"
  eve_say "${C_DIM}  platform: $(eve_platform) · root: $EVE_ROOT${C_RESET}"
  eve_say ""

  # --- awaken each subsystem (report presence) ---
  _eve_probe "QBIT NOVA quantum-core (python)" test -n "$(eve_python)"
  _eve_probe "QBIT language pipeline" test -f "$EVE_ROOT/tools/qbit_nova_run_v01.py"
  _eve_probe "Nova Guard shields" test -f "$EVE_ROOT/tools/qbit_nova_guard_approval_v06.py"
  _eve_probe "Carry-On command gateway" test -d "$EVE_ROOT/carryon/carryon_gateway"
  _eve_probe "WhatsApp voice engine" test -d "$EVE_ROOT/carryon/whatsapp_voice"
  _eve_probe "Media forge (ffmpeg)" command -v ffmpeg
  _eve_probe "Node bridge realm" command -v node

  eve_say ""
  if [ "$boot" -eq 1 ]; then
    eve_say "${C_B}${C_CYAN}  ⟪  IGNITING LIVE DAEMONS  ⟫${C_RESET}"
    if [ -n "${CARRYON_GATEWAY_SECRET:-}${CARRYON_GATEWAY_KEYFILE:-}" ]; then
      eve_cmd_gateway start
    else
      eve_warn "gateway not ignited — set CARRYON_GATEWAY_SECRET to enable it"
    fi
    eve_cmd_whatsapp start
    eve_say ""
    eve_cmd_status
    eve_say ""
    eve_ok "The world breathes. Stop everything with:  ./eve down"
  else
    eve_ok "World mapped. Ignite the live daemons with:  ${C_B}./eve mythos --boot${C_RESET}"
    eve_info "Or piece by piece:  ./eve gateway start · ./eve whatsapp start · ./eve status"
  fi
}
