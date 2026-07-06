#!/usr/bin/env bash
# =============================================================================
# Claude Code — universal installer for Terminal (glibc Linux) AND Termux
# -----------------------------------------------------------------------------
# Why this exists: on Termux, Node reports platform "android", so npm never
# downloads Claude Code's glibc linux-arm64 native binary -> you get:
#     "Error: claude native binary not installed."
# Even if forced, that binary is glibc-linked and won't run under Termux's
# bionic libc. The reliable fix on Android is a glibc userland via proot-distro.
#
# This script auto-detects the environment and does the right thing:
#   * glibc Linux (Pi5, servers, WSL, the "terminal") -> native npm install
#   * Termux (Android)                                 -> proot-distro Ubuntu,
#     install Claude Code inside it, and drop a `claude` launcher on the Termux
#     side that transparently runs it in the current directory.
#
# Usage:
#   bash install.sh            # auto
#   bash install.sh --glibc    # force the plain-Linux path
#   bash install.sh --termux   # force the Termux/proot path
# =============================================================================
set -euo pipefail

# ---- config (override via env) ----
DISTRO="${CLAUDE_DISTRO:-ubuntu}"          # proot-distro alias for Termux path
NODE_MAJOR="${CLAUDE_NODE_MAJOR:-20}"      # Node major to install inside distro
PKG="@anthropic-ai/claude-code"

log()  { printf '\033[1;36m[claude-setup]\033[0m %s\n' "$*" >&2; }
warn() { printf '\033[1;33m[claude-setup] WARN:\033[0m %s\n' "$*" >&2; }
die()  { printf '\033[1;31m[claude-setup] ERROR:\033[0m %s\n' "$*" >&2; exit 1; }

is_termux() {
  [ -n "${TERMUX_VERSION:-}" ] || [ -d /data/data/com.termux ] \
    || { command -v uname >/dev/null && [ "$(uname -o 2>/dev/null)" = "Android" ]; }
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# -----------------------------------------------------------------------------
# Path A: plain glibc Linux (the "terminal" — Pi5, server, WSL)
# -----------------------------------------------------------------------------
install_glibc() {
  log "Environment: glibc Linux. Installing Claude Code natively via npm."
  command -v node >/dev/null || die "Node.js not found. Install Node 18+ first."
  local major; major="$(node -p 'process.versions.node.split(".")[0]')"
  [ "$major" -ge 18 ] || die "Node $major too old; Claude Code needs Node >= 18."

  # --allow-scripts lets the postinstall fetch the native binary (npm >= 10 nags
  # about it; older npm just runs it). Try both call styles for compatibility.
  log "npm install -g $PKG (allowing postinstall)"
  npm install -g --allow-scripts="$PKG" "$PKG" 2>/dev/null \
    || npm install -g "$PKG"

  # Belt and suspenders: run the postinstall explicitly if the binary is missing.
  local root; root="$(npm root -g)"
  if [ -f "$root/$PKG/install.cjs" ]; then
    node "$root/$PKG/install.cjs" || warn "postinstall returned non-zero (may already be installed)"
  fi

  command -v claude >/dev/null \
    && log "Done. Run: claude" \
    || warn "claude not on PATH yet — add \"$(npm bin -g 2>/dev/null || echo "$root/.bin")\" to PATH."
}

# -----------------------------------------------------------------------------
# Path B: Termux (Android) via proot-distro glibc userland
# -----------------------------------------------------------------------------
install_termux() {
  log "Environment: Termux/Android. Setting up a glibc userland (proot-distro/$DISTRO)."

  log "Updating Termux packages + installing proot-distro"
  pkg update -y >/dev/null 2>&1 || warn "pkg update had warnings (continuing)"
  pkg install -y proot-distro >/dev/null

  if ! proot-distro list --installed 2>/dev/null | grep -q "^$DISTRO"; then
    log "Installing $DISTRO rootfs (one-time, downloads ~100-150MB)"
    proot-distro install "$DISTRO"
  else
    log "$DISTRO already installed — reusing it."
  fi

  log "Installing Node $NODE_MAJOR + Claude Code inside $DISTRO"
  proot-distro login "$DISTRO" -- bash -lc "
    set -e
    export DEBIAN_FRONTEND=noninteractive
    apt-get update -y
    apt-get install -y curl ca-certificates git
    if ! command -v node >/dev/null || [ \"\$(node -p 'process.versions.node.split(\".\")[0]')\" -lt 18 ]; then
      curl -fsSL https://deb.nodesource.com/setup_${NODE_MAJOR}.x | bash -
      apt-get install -y nodejs
    fi
    npm install -g ${PKG}
    claude --version || node \"\$(npm root -g)/${PKG}/install.cjs\"
    claude --version
  "

  install_launcher
  log "Done. Run:  claude        (it drops you into $DISTRO in your current dir)"
}

# Install a Termux-side `claude` launcher that runs the real binary inside the
# distro, binding the current working directory so files are shared 1:1.
install_launcher() {
  local prefix="${PREFIX:-/data/data/com.termux/files/usr}"
  local dest="$prefix/bin/claude"
  log "Installing launcher -> $dest"
  sed "s|@@DISTRO@@|$DISTRO|g" "$SCRIPT_DIR/bin/claude-launcher.template" > "$dest"
  chmod +x "$dest"
}

# -----------------------------------------------------------------------------
main() {
  case "${1:-auto}" in
    --glibc)  install_glibc ;;
    --termux) install_termux ;;
    auto|"")  if is_termux; then install_termux; else install_glibc; fi ;;
    *)        die "unknown arg: $1 (use --glibc | --termux)" ;;
  esac
}
main "${1:-auto}"
