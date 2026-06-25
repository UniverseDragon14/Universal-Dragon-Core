#!/usr/bin/env sh
set -eu

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$ROOT"

mkdir -p dist

NAME="qbit-nova-v02-release"
OUT="dist/${NAME}.tar.gz"
SHA="dist/${NAME}.sha256"

tar -czf "$OUT"   docs   examples   tools   tests

sha256sum "$OUT" > "$SHA"

echo "QBIT_NOVA_RELEASE_ARCHIVE_V02"
echo "ARCHIVE: $OUT"
cat "$SHA"
echo "QBIT_NOVA_RELEASE_ARCHIVE_V02_GREEN"
