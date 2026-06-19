#!/usr/bin/env bash
set -euo pipefail

PORT="${UD_TERMINAL_PORT:-7681}"

if ! command -v tailscale >/dev/null 2>&1; then
  echo "ERROR: tailscale command not found. Install Tailscale on the Pi5 first."
  echo "Then log in with: sudo tailscale up"
  exit 1
fi

if ! command -v ttyd >/dev/null 2>&1; then
  echo "ERROR: ttyd not found. Run setup first:"
  echo "  bash ud-terminal/scripts/setup-pi-ttyd.sh"
  exit 1
fi

echo "Checking local ttyd on http://127.0.0.1:${PORT} ..."
if command -v curl >/dev/null 2>&1; then
  if ! curl -fsI "http://127.0.0.1:${PORT}" >/dev/null 2>&1; then
    echo "Local ttyd does not seem reachable. Restarting user service..."
    systemctl --user restart ud-terminal.service || true
    sleep 2
  fi
fi

echo
echo "Starting Tailscale Serve for UD Terminal."
echo "This should print a private HTTPS URL available only inside your tailnet."
echo "Open that URL on iPhone after connecting the iPhone to Tailscale."
echo
echo "IMPORTANT: Do not use Funnel or public port forwarding for this terminal."
echo

tailscale serve "${PORT}"
