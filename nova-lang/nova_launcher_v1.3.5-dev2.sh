#!/data/data/com.termux/files/usr/bin/bash

ROOT="$PREFIX/share/nova"
CORE="$ROOT/nova.py"
QBIT="$ROOT/adapters/qbit/qsim.py"
ADAPTER="$ROOT/adapters/adapter_check.sh"

show_version(){
  echo "NOVA v1.3.5-dev"
  echo "Identity : Universal Dragon NOVA"
  echo "Runtime  : Portable Multi-Engine Tool-Language Runtime"
  echo "Engines  : nova-core, qbit, python, bash, node, sqlite, C, C++, Rust, Java"
  echo "Mode     : Termux Portable Public Package"
}

show_help(){
  echo "NOVA Portable Router v1.3.5-dev"
  echo "Commands:"
  echo "  nova version"
  echo "  nova doctor"
  echo "  nova adapter"
  echo "  nova py 'print(123)'"
  echo "  nova qbit file.qnova"
  echo "  nova run file"
  echo "  nova examples"
}

show_examples(){
  echo "$ROOT/examples"
  ls -la "$ROOT/examples" 2>/dev/null || true
}

run_file(){
  file="$1"
  [ -f "$file" ] || { echo "File not found: $file"; exit 1; }

  first="$(head -n 1 "$file")"
  ext="${file##*.}"

  case "$first" in
    "# nova-engine: qbit"*) engine="qbit" ;;
    "# nova-engine: python"*) engine="python" ;;
    "# nova-engine: node"*) engine="node" ;;
    "# nova-engine: bash"*) engine="bash" ;;
    "# nova-engine: sqlite"*) engine="sqlite" ;;
    *) engine="$ext" ;;
  esac

  case "$engine" in
    qnova|qbit) python "$QBIT" "$file" ;;
    py|python) python "$file" ;;
    js|node) node "$file" ;;
    sh|bash) bash "$file" ;;
    sql|sqlite) sqlite3 < "$file" ;;
    nova) python "$CORE" run "$file" ;;
    *) echo "Unknown engine for: $file" ;;
  esac
}

ensure_home(){
  ROOT_HOME="$HOME/nova-lang"
  mkdir -p "$ROOT_HOME/memory" "$ROOT_HOME/backups" "$ROOT_HOME/lib" "$ROOT_HOME/apps" "$ROOT_HOME/tools" "$ROOT_HOME/adapters"
  [ -f "$ROOT_HOME/memory/memory.txt" ] || echo "NOVA memory initialized" > "$ROOT_HOME/memory/memory.txt"
  [ -f "$ROOT_HOME/memory/history.txt" ] || echo "$(date '+%Y-%m-%d %H:%M:%S') | NOVA fresh home initialized" > "$ROOT_HOME/memory/history.txt"
}

case "$1" in
  version)
    show_version
    ;;
  help|--help|-h|"")
    show_help
    ;;
  adapter)
    bash "$ADAPTER"
    ;;
  doctor)
    ensure_home
    show_version
    echo
    python "$CORE" doctor
    echo
    bash "$ADAPTER"
    ;;
  py)
    shift
    python -c "$*"
    ;;
  qbit|q)
    shift
    python "$QBIT" "$@"
    ;;
  run)
    shift
    run_file "$1"
    ;;
  examples)
    ensure_home
    show_examples
    ;;
  *)
    ensure_home
    python "$CORE" "$@"
    ;;
esac
