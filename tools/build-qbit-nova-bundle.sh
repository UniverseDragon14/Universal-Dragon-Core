#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)

STAMP=$(date +%Y%m%d_%H%M%S)
DEST="${1:-$HOME/qbit-nova-release-bundle-$STAMP}"

rm -rf "$DEST"
mkdir -p "$DEST"

copy_file() {
  rel="$1"
  src="$ROOT/$rel"
  dst="$DEST/$rel"

  if [ ! -f "$src" ]; then
    echo "Missing bundle file: $rel"
    exit 1
  fi

  mkdir -p "$(dirname "$dst")"
  cp -p "$src" "$dst"
}

copy_file "README.md"
copy_file "NOVA_QBIT_VERSION"

copy_file "tools/nova_cli.ud"
copy_file "tools/qbit-nova"
copy_file "tools/install-qbit-nova.sh"

copy_file "engine/qbit_nova_v07_engine.py"
copy_file "engine/qbit_nova_v08_tokenizer.py"
copy_file "engine/qbit_nova_v09_token_parser.py"
copy_file "engine/qbit_nova_v09_pipeline.py"

copy_file "nova-lang/v2/nova2_run.py"
copy_file "nova-lang/v2/nova2_seed.py"
copy_file "nova-lang/v2/nova2_quantum_syntax.py"

copy_file "examples/v2/qbit_nova_world.ud"
copy_file "examples/v2/qbit_nova_v07_native_zero.ud"
copy_file "examples/v2/qbit_nova_v07_native_one.ud"

chmod +x "$DEST/tools/qbit-nova" "$DEST/tools/install-qbit-nova.sh" "$DEST/tools/nova_cli.ud" 2>/dev/null || true

cat > "$DEST/QBIT_NOVA_RELEASE_BUNDLE.txt" <<EOF
QBIT NOVA Release Bundle v1.3

UD means Universal Dragon.
Creator: Aslam
Team: Askutty
Brain: NovaKutty
Language: QBIT NOVA
Source extension: .ud

Marker:
QBIT_NOVA_V13_RELEASE_BUNDLE
EOF

echo "QBIT NOVA release bundle built:"
echo "$DEST"
echo "QBIT_NOVA_V13_BUNDLE_BUILT"
