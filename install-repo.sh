#!/data/data/com.termux/files/usr/bin/bash
set -e

ROOT="$HOME/ud-github-sync"
BRANCH="nova-v1.3.5-dev"
REPO="https://github.com/UniverseDragon14/Universal-Dragon-Core.git"

echo "🐉 Adding Universal Dragon NOVA..."

pkg install -y python bash curl git >/dev/null

mkdir -p "$PREFIX/etc/apt/sources.list.d"
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
set -e

ROOT="$HOME/ud-github-sync"
RUNNER="$ROOT/nova-lang/v2/nova2_run.py"

cmd="${1:-}"

case "$cmd" in
  run)
    shift
    [ -n "${1:-}" ] || { echo "Usage: nova run <file.nova>"; exit 1; }
    python3 "$RUNNER" "$1"
    ;;

  qbit)
    shift
    [ -n "${1:-}" ] || { echo "Usage: nova qbit <file.nova>"; exit 1; }
    python3 "$RUNNER" "$1"
    ;;

  note)
    shift
    mkdir -p "$HOME/nova-lang/notes"
    echo "$(date '+%Y-%m-%d %H:%M:%S') $*" >> "$HOME/nova-lang/notes/nova_notes.log"
    echo "Noted."
    ;;

  backup)
    mkdir -p "$HOME/nova-lang/backups"
    tar -czf "$HOME/nova-lang/backups/backup_$(date +%Y%m%d_%H%M%S).tar.gz" "$ROOT" "$HOME/nova-lang" 2>/dev/null || true
    ls -lh "$HOME/nova-lang/backups" | tail -3
    ;;

  version|doctor)
    echo "NOVA commands:"
    echo "  nova run <file.nova>"
    echo "  nova qbit <file.nova>"
    echo "  nova note <message>"
    echo "  nova backup"
    ;;

  *)
    echo "NOVA commands:"
    echo "  nova run <file.nova>"
    echo "  nova qbit <file.nova>"
    echo "  nova note <message>"
    echo "  nova backup"
    ;;
esac
NOVAEOF

chmod +x "$PREFIX/bin/nova"

cat > "$PREFIX/share/nova/examples/qbit_test.qnova" <<'QBEOF'
qbit dragon = |0>
h dragon
measure dragon
QBEOF

echo "✅ NOVA installed"
nova doctor
