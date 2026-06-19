#!/usr/bin/env bash
set -euo pipefail

NOVA_BIN="$(command -v nova || true)"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
V2_RUNNER="$REPO_DIR/nova-lang/v2/nova2_run.py"

if [ -z "$NOVA_BIN" ]; then
  echo "ERROR: nova command not found."
  exit 1
fi

if [ ! -f "$V2_RUNNER" ]; then
  echo "ERROR: NOVA v2 runner not found: $V2_RUNNER"
  exit 1
fi

BACKUP="$HOME/nova-bin-backup-$(date +%Y%m%d_%H%M%S)"
cp "$NOVA_BIN" "$BACKUP"

python3 - <<PY
from pathlib import Path

p = Path("$NOVA_BIN")
s = p.read_text()

old = 'nova) python "$CORE" run "$file" ;;'

new = '''nova)
      if [ -f "$PWD/nova-lang/v2/nova2_run.py" ]; then
        python "$PWD/nova-lang/v2/nova2_run.py" "$file"
      elif [ -f "$HOME/ud-github-sync/nova-lang/v2/nova2_run.py" ]; then
        python "$HOME/ud-github-sync/nova-lang/v2/nova2_run.py" "$file"
      else
        python "$CORE" run "$file"
      fi
      ;;'''

if old not in s and 'nova2_run.py' in s:
    print("NOVA wrapper already routes to NOVA v2.")
elif old in s:
    p.write_text(s.replace(old, new))
    print("NOVA wrapper patched: nova run now routes .nova files to NOVA v2.")
else:
    print("ERROR: patch target not found. Manual inspection needed.")
    raise SystemExit(1)
PY

chmod +x "$NOVA_BIN"

echo "Backup saved: $BACKUP"
echo "Test:"
echo "  nova run examples/v2/qbit_bell_cnot_test.nova"
