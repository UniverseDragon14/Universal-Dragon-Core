#!/usr/bin/env bash
set -euo pipefail

SERVICE_DIR="$HOME/.config/systemd/user"
SERVICE_FILE="$SERVICE_DIR/ud-terminal.service"
REPO_SERVICE_FILE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/systemd/ud-terminal.service"

echo "UD Terminal setup starting..."
echo "This will install ttyd and create a user-level systemd service."

if ! command -v apt >/dev/null 2>&1; then
  echo "ERROR: apt not found. This setup is for Raspberry Pi OS / Debian-based systems."
  exit 1
fi

if ! command -v ttyd >/dev/null 2>&1; then
  echo "Installing ttyd..."
  sudo apt update
  sudo apt install -y ttyd
else
  echo "ttyd already installed."
fi

mkdir -p "$SERVICE_DIR"
cp "$REPO_SERVICE_FILE" "$SERVICE_FILE"

systemctl --user daemon-reload
systemctl --user enable --now ud-terminal.service

echo
echo "UD Terminal local service started."
echo "Local URL: http://127.0.0.1:7681"
echo
echo "Check status:"
echo "  systemctl --user status ud-terminal.service --no-pager"
echo
echo "Next: run this to expose privately inside your Tailscale tailnet:"
echo "  bash ud-terminal/scripts/start-tailnet-url.sh"
