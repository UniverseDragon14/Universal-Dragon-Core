#!/usr/bin/env sh
set -eu

PREFIX="${QBIT_NOVA_PREFIX:-$HOME/.local}"

if [ "$#" -gt 0 ]; then
  case "$1" in
    --prefix)
      if [ "$#" -lt 2 ]; then
        echo "Usage: ./tools/install-qbit-nova.sh --prefix <path>"
        exit 1
      fi
      PREFIX="$2"
      ;;
    *)
      PREFIX="$1"
      ;;
  esac
fi

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)

BIN_DIR="$PREFIX/bin"
mkdir -p "$BIN_DIR"

cat > "$BIN_DIR/qbit-nova" <<EOF
#!/usr/bin/env sh
exec python3 "$ROOT/tools/nova_cli.ud" "\$@"
EOF

chmod +x "$BIN_DIR/qbit-nova"

echo "QBIT NOVA installer"
echo "root: $ROOT"
echo "installed: $BIN_DIR/qbit-nova"
echo
echo "Run:"
echo "  $BIN_DIR/qbit-nova doctor"
echo

"$BIN_DIR/qbit-nova" doctor >/dev/null

echo "QBIT_NOVA_V12_INSTALLER_GREEN"
