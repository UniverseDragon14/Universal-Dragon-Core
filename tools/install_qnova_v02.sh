#!/usr/bin/env sh
set -eu

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"

TARGET_BIN="${QBIT_NOVA_INSTALL_BIN:-}"

if [ -z "$TARGET_BIN" ]; then
  if [ -n "${PREFIX:-}" ] && [ -d "$PREFIX/bin" ] && [ -w "$PREFIX/bin" ]; then
    TARGET_BIN="$PREFIX/bin"
  else
    TARGET_BIN="$HOME/.local/bin"
  fi
fi

mkdir -p "$TARGET_BIN"

TARGET="$TARGET_BIN/qnova"

if [ -e "$TARGET" ]; then
  BACKUP="$TARGET.backup.$(date +%Y%m%d_%H%M%S)"
  cp "$TARGET" "$BACKUP"
  echo "BACKUP_CREATED: $BACKUP"
fi

cat > "$TARGET" <<EOF
#!/usr/bin/env sh
set -eu
ROOT="$ROOT"
python3 "\$ROOT/tools/qbit_nova_syntax_v02.py" "\$@"
EOF

chmod +x "$TARGET"

echo "QBIT_NOVA_INSTALLER_V02"
echo "INSTALLED: $TARGET"

"$TARGET" "$ROOT/examples/v2/qbit_nova_cli_launcher_v02.qnova" > "$ROOT/.tmp/qnova_install_test_output.txt"

grep -q "QBIT_NOVA_SYNTAX_V02_GREEN" "$ROOT/.tmp/qnova_install_test_output.txt"
grep -q "QBIT_NOVA_CLI_LAUNCHER_V02" "$ROOT/.tmp/qnova_install_test_output.txt"

echo "QBIT_NOVA_INSTALLER_V02_GREEN"
