#!/data/data/com.termux/files/usr/bin/bash
set -e

ROOT="$HOME/ud-github-sync"
BRANCH="nova-v1.3.5-dev"
REPO="https://github.com/UniverseDragon14/Universal-Dragon-Core.git"

echo "🐉 Installing Universal Dragon NOVA..."

pkg install -y python bash curl git >/dev/null

mkdir -p "$PREFIX/share/nova/examples"

if [ -d "$ROOT/.git" ]; then
  cd "$ROOT"
  git fetch origin "$BRANCH" || true
  git checkout "$BRANCH" || true
  git pull origin "$BRANCH" || true
else
  git clone -b "$BRANCH" "$REPO" "$ROOT"
fi

cat > "$PREFIX/bin/nova" <<'NOVAEOF'
#!/data/data/com.termux/files/usr/bin/bash
ROOT="$HOME/ud-github-sync"
python3 "$ROOT/tools/nova_cli.ud" "$@"
NOVAEOF

chmod +x "$PREFIX/bin/nova"

cat > "$PREFIX/share/nova/examples/qbit_test.qnova" <<'QBEOF'
qbit dragon = |0>
h dragon
measure dragon
QBEOF

echo "✅ NOVA installed"
nova doctor
nova qbit "$PREFIX/share/nova/examples/qbit_test.qnova"
