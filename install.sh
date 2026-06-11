#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "🐉 Universal Dragon NOVA Installer"
echo "Installing NOVA portable package for Termux..."

pkg update -y
pkg install -y python bash curl

TMP="$PREFIX/tmp/nova_1.3.5_dev2_all.deb"
URL="https://raw.githubusercontent.com/UniverseDragon14/Universal-Dragon-Core/nova-v1.3.5-dev2/nova-lang/packages/nova_1.3.5_dev2_all.deb"

echo "Downloading NOVA package..."
curl -L "$URL" -o "$TMP"

echo "Installing NOVA..."
dpkg -i "$TMP" || apt -f install -y

echo
echo "Testing NOVA..."
nova version
nova doctor
nova run "$PREFIX/share/nova/examples/qbit_test.qnova"
nova py 'print("NOVA install test GREEN")'

echo
echo "✅ NOVA installed successfully."
echo "Run: nova help"
