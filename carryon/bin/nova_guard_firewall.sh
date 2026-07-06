#!/usr/bin/env bash
# Example Nova Guard "firewall shield". Replace the body with your real rules.
# Invoked by the gateway as: nova_guard_firewall.sh on|off
set -euo pipefail
MODE="${1:-on}"
echo "[nova-guard] firewall shield -> ${MODE}"
# Example (Linux w/ nftables). Guarded behind a dry-run flag by default.
# if [ "$MODE" = "on" ]; then
#   sudo nft add table inet nova_guard 2>/dev/null || true
#   ...
# fi
