#!/usr/bin/env bash
# eve doctor — inspect the world and report readiness of every subsystem.

eve_cmd_doctor() {
  eve_say "${C_B}EVE · world readiness${C_RESET}"
  eve_say ""
  eve_say "${C_DIM}-- platform --${C_RESET}"
  eve_info "root:     $EVE_ROOT"
  eve_info "platform: $(eve_platform)   ($(uname -om 2>/dev/null || echo '?'))"

  local py; py="$(eve_python)"
  eve_say ""
  eve_say "${C_DIM}-- toolchain --${C_RESET}"
  [ -n "$py" ] && eve_ok "python: $($py --version 2>&1)" || eve_err "python missing (pkg install python)"
  command -v node >/dev/null && eve_ok "node: $(node -v)" || eve_warn "node missing (needed for WhatsApp bridge)"
  command -v ffmpeg >/dev/null && eve_ok "ffmpeg present" || eve_warn "ffmpeg missing (needed for media/voice)"
  command -v git >/dev/null && eve_ok "git present" || eve_warn "git missing"

  eve_say ""
  eve_say "${C_DIM}-- subsystems --${C_RESET}"
  [ -f "$EVE_ROOT/tools/qbit_nova_run_v01.py" ] && eve_ok "QBIT NOVA language engine" || eve_err "qbit nova engine not found"
  [ -f "$EVE_ROOT/tools/qbit_nova_guard_approval_v06.py" ] && eve_ok "Nova Guard v0.6" || eve_warn "Nova Guard not found"
  [ -d "$EVE_ROOT/carryon" ] && eve_ok "Carry-On core (gateway/whatsapp/media)" || eve_warn "carryon/ not found"

  eve_say ""
  if [ -n "$py" ]; then
    eve_ok "EVE is ready. Try:  ${C_B}./eve mythos${C_RESET}"
  else
    eve_err "Install python first, then re-run ./eve doctor"
  fi
}
