#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)

OUT_DIR="${1:-$HOME/qbit-nova-release-artifacts}"
STAMP=$(date +%Y%m%d_%H%M%S)
VERSION="v1.4.0-dev"

mkdir -p "$OUT_DIR"

BUNDLE="$OUT_DIR/qbit-nova-bundle-$VERSION-$STAMP"
ARCHIVE="$OUT_DIR/qbit-nova-release-$VERSION-$STAMP.tar.gz"
CHECKSUM="$ARCHIVE.sha256"
MANIFEST="$OUT_DIR/QBIT_NOVA_RELEASE_MANIFEST_${VERSION}_${STAMP}.txt"

"$ROOT/tools/build-qbit-nova-bundle.sh" "$BUNDLE"

tar -czf "$ARCHIVE" -C "$(dirname "$BUNDLE")" "$(basename "$BUNDLE")"

sha256sum "$ARCHIVE" > "$CHECKSUM"

cat > "$MANIFEST" <<EOF
QBIT NOVA Release Archive v1.4

UD means Universal Dragon.
Creator: Aslam
Team: Askutty
Brain: NovaKutty
Language: QBIT NOVA
Source extension: .ud
Version: $VERSION

Archive:
$ARCHIVE

Checksum:
$CHECKSUM

Install after extract:
./tools/install-qbit-nova.sh --prefix "\$HOME/.local"

Run:
\$HOME/.local/bin/qbit-nova doctor
\$HOME/.local/bin/qbit-nova native examples/v2/qbit_nova_v07_native_zero.ud
\$HOME/.local/bin/qbit-nova ir examples/v2/qbit_nova_v07_native_zero.ud

Proof route:
release archive
-> checksum verify
-> extract
-> install
-> doctor Runner OK
-> run .ud
-> ir command

Marker:
QBIT_NOVA_V14_RELEASE_ARCHIVE
EOF

echo "QBIT NOVA release archive built"
echo "archive: $ARCHIVE"
echo "checksum: $CHECKSUM"
echo "manifest: $MANIFEST"
echo "QBIT_NOVA_V14_RELEASE_ARCHIVE_BUILT"
