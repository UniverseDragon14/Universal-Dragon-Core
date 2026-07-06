#!/usr/bin/env bash
# Claude Code environment doctor — prints what's installed and what's missing,
# then tells you exactly which install path to run. Safe to run anytime.
set -uo pipefail

ok()   { printf '  \033[1;32m✓\033[0m %s\n' "$*"; }
no()   { printf '  \033[1;31m✗\033[0m %s\n' "$*"; }
info() { printf '  \033[1;36m•\033[0m %s\n' "$*"; }

is_termux() {
  [ -n "${TERMUX_VERSION:-}" ] || [ -d /data/data/com.termux ] \
    || { command -v uname >/dev/null && [ "$(uname -o 2>/dev/null)" = "Android" ]; }
}

echo "=== Claude Code doctor ==="
echo "-- platform --"
info "uname:   $(uname -om 2>/dev/null || echo '?')"
if command -v node >/dev/null; then
  NODE_PLAT="$(node -p 'process.platform + "/" + process.arch' 2>/dev/null || echo '?')"
else
  NODE_PLAT="node missing"
fi
info "node.platform: $NODE_PLAT"
if is_termux; then info "detected: TERMUX (Android)"; else info "detected: glibc Linux (terminal)"; fi

echo "-- toolchain --"
command -v node >/dev/null && ok "node $(node -v)" || no "node not found"
command -v npm  >/dev/null && ok "npm $(npm -v)"  || no "npm not found"
command -v git  >/dev/null && ok "git present"    || no "git not found"

echo "-- claude --"
if command -v claude >/dev/null; then
  ok "claude on PATH: $(command -v claude)"
  claude --version 2>/dev/null && ok "claude runs" || no "claude present but won't run (native binary?)"
else
  no "claude not on PATH"
fi

if is_termux; then
  echo "-- termux/proot --"
  command -v proot-distro >/dev/null && ok "proot-distro installed" || no "proot-distro missing (pkg install proot-distro)"
  if command -v proot-distro >/dev/null; then
    proot-distro list --installed 2>/dev/null | grep -q ubuntu \
      && ok "ubuntu rootfs installed" || info "ubuntu rootfs not installed yet"
  fi
fi

echo
echo "=== recommendation ==="
if is_termux; then
  echo "  Termux detected. Run:   bash install.sh --termux"
  echo "  (npm-global install cannot work here — Android has no glibc native binary.)"
else
  echo "  Terminal detected. Run:  bash install.sh --glibc"
fi
