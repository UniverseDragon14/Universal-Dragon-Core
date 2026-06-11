#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "🐉 Adding Universal Dragon NOVA repo..."

pkg update -y
pkg install -y python bash curl

REPO="https://raw.githubusercontent.com/UniverseDragon14/Universal-Dragon-Core/nova-v1.3.5-dev/repo"

echo "deb [trusted=yes] $REPO ./" > "$PREFIX/etc/apt/sources.list.d/nova.list"

apt update
pkg install -y nova

echo
nova version
nova doctor
nova run "$PREFIX/share/nova/examples/qbit_test.qnova"
nova py 'print("NOVA pkg install GREEN")'

echo
echo "✅ Done. From now on: pkg install nova"
