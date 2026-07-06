#!/usr/bin/env bash
# EVE shared environment layer. Sourced by `eve` and every eve-core/*.sh module.
# Resolves paths, detects Termux vs glibc, and finds a working python/node.
# Nothing here runs anything destructive — pure detection and helpers.

# --- resolve repo root (this file lives in <root>/eve-core/) ---
EVE_CORE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EVE_ROOT="$(cd "$EVE_CORE_DIR/.." && pwd)"
export EVE_ROOT EVE_CORE_DIR

# --- version ---
EVE_VERSION="$(cat "$EVE_ROOT/eve-core/VERSION" 2>/dev/null || echo "0.1.0")"
export EVE_VERSION

# --- colors (disabled when not a tty or NO_COLOR set) ---
if [ -t 1 ] && [ -z "${NO_COLOR:-}" ]; then
  C_RESET=$'\033[0m'; C_DIM=$'\033[2m'; C_B=$'\033[1m'
  C_CYAN=$'\033[1;36m'; C_MAG=$'\033[1;35m'; C_GRN=$'\033[1;32m'
  C_YEL=$'\033[1;33m'; C_RED=$'\033[1;31m'; C_BLU=$'\033[1;34m'
else
  C_RESET=""; C_DIM=""; C_B=""; C_CYAN=""; C_MAG=""; C_GRN=""; C_YEL=""; C_RED=""; C_BLU=""
fi
export C_RESET C_DIM C_B C_CYAN C_MAG C_GRN C_YEL C_RED C_BLU

# --- logging helpers (all to stderr; stdout stays clean for data) ---
eve_say()  { printf '%s\n' "$*" >&2; }
eve_ok()   { printf '%s  ✦ %s%s\n' "$C_GRN" "$*" "$C_RESET" >&2; }
eve_info() { printf '%s  › %s%s\n' "$C_CYAN" "$*" "$C_RESET" >&2; }
eve_warn() { printf '%s  ! %s%s\n' "$C_YEL" "$*" "$C_RESET" >&2; }
eve_err()  { printf '%s  ✗ %s%s\n' "$C_RED" "$*" "$C_RESET" >&2; }
eve_die()  { eve_err "$*"; exit 1; }

# --- platform detection ---
eve_is_termux() {
  [ -n "${TERMUX_VERSION:-}" ] || [ -d /data/data/com.termux ] \
    || { command -v uname >/dev/null && [ "$(uname -o 2>/dev/null)" = "Android" ]; }
}

eve_platform() { eve_is_termux && echo "termux" || echo "glibc"; }

# --- python resolver (repo uses python3) ---
eve_python() {
  if [ -n "${EVE_PYTHON:-}" ]; then echo "$EVE_PYTHON"; return; fi
  for c in python3 python; do command -v "$c" >/dev/null && { echo "$c"; return; }; done
  echo ""
}

# Run a python module from the repo root so `carryon.*` and `tools/*` import.
eve_pyrun() {
  local py; py="$(eve_python)"
  [ -n "$py" ] || eve_die "python3 not found. Install it (pkg install python)."
  ( cd "$EVE_ROOT" && "$py" "$@" )
}
