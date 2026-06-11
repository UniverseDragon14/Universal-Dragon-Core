#!/data/data/com.termux/files/usr/bin/bash
ROOT="$HOME/nova-lang"
OUT="$ROOT/adapters/ADAPTER_STATUS.txt"

mkdir -p "$ROOT/adapters"

{
  echo "NOVA ADAPTER STATUS"
  echo "Generated: $(date)"
  echo

  check() {
    name="$1"
    cmd="$2"
    if command -v "$cmd" >/dev/null 2>&1; then
      echo "READY  $name -> $(command -v "$cmd")"
    else
      echo "MISSING $name -> $cmd"
    fi
  }

  check "Bash" bash
  check "Python" python
  check "Node.js" node
  check "C clang" clang
  check "C++ g++" g++
  check "Rust" rustc
  check "Java" java
  check "SQLite" sqlite3
} | tee "$OUT"

echo
echo "Saved: $OUT"
