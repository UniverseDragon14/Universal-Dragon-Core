#!/data/data/com.termux/files/usr/bin/bash

ROOT="$HOME/nova-lang"
CORE="$ROOT/nova.py"
QBIT="$ROOT/adapters/qbit/qsim.py"

engine_from_header() {
  file="$1"
  head -n 8 "$file" 2>/dev/null | grep -i "nova-engine:" | head -n 1 | cut -d: -f2 | tr -d ' \r'
}

run_universal() {
  file="$1"
  shift || true

  [ -z "$file" ] && echo "Use: nova run file.qnova|file.py|file.js|file.sh|file.sql|file.nova" && exit 1
  [ ! -f "$file" ] && echo "File not found: $file" && exit 1

  engine="$(engine_from_header "$file")"

  if [ -z "$engine" ]; then
    case "$file" in
      *.qnova) engine="qbit" ;;
      *.py) engine="python" ;;
      *.js) engine="node" ;;
      *.sh) engine="bash" ;;
      *.sql) engine="sqlite" ;;
      *.nova) engine="nova" ;;
      *) engine="nova" ;;
    esac
  fi

  case "$engine" in
    qbit|quantum) exec python "$QBIT" "$file" "$@" ;;
    python|py) exec python "$file" "$@" ;;
    node|js) exec node "$file" "$@" ;;
    bash|sh) exec bash "$file" "$@" ;;
    sqlite|sql) exec sqlite3 "$ROOT/memory/nova.db" < "$file" ;;
    nova|core) exec python "$CORE" run "$file" "$@" ;;
    *) echo "Unknown NOVA engine: $engine"; exit 1 ;;
  esac
}

show_notes_v134(){
  ROOT="$HOME/nova-lang"
  H="$ROOT/memory/history.txt"
  echo "NOVA NOTES v1.3.4-dev"
  echo "Latest saved notes:"
  echo
  if [ -f "$H" ]; then
    tail -n 25 "$H"
  else
    echo "No history file found: $H"
  fi
}

show_help_v134(){
  echo "NOVA Launcher Router v1.3.4-dev"
  echo "Commands:"
  echo "  nova version"
  echo "  nova doctor"
  echo "  nova note message"
  echo "  nova notes"
  echo "  nova router"
  echo "  nova adapter"
  echo "  nova run file"
  echo "  nova qbit file.qnova"
  echo "  nova py 'print(123)'"
}

doctor_combined_v134(){
  ROOT="$HOME/nova-lang"
  CORE="$ROOT/nova.py"
  echo "NOVA DOCTOR + ADAPTER v1.3.4-dev"
  echo
  python "$CORE" doctor
  echo
  if [ -x "$ROOT/adapters/adapter_check.sh" ]; then
    "$ROOT/adapters/adapter_check.sh"
  else
    echo "Adapter checker missing: $ROOT/adapters/adapter_check.sh"
  fi
}

show_version_v134(){
  echo "NOVA v1.3.4-dev"
  echo "Identity : Universal Dragon NOVA"
  echo "Runtime  : Multi-Engine Tool-Language Runtime"
  echo "Engines  : nova-core, qbit, python, bash, node, sqlite, C, C++, Rust, Java"
  echo "Mode     : Termux Mobile Field Lab"
}

case "$1" in
  router|router-version)
    echo "NOVA Launcher Router v1.3.4-dev"
    echo "Routes: adapter, py, qbit, run, notes, help"
    ;;

  version)
    show_version_v134
    ;;

  doctor)
    shift
    doctor_combined_v134 "$@"
    ;;

  adapter)
    shift
    exec "$ROOT/adapters/adapter_check.sh" "$@"
    ;;

  py)
    shift
    exec python -c "$*"
    ;;

  qbit|q)
    shift
    exec python "$QBIT" "$@"
    ;;

  run)
    shift
    run_universal "$@"
    ;;

  notes)
    show_notes_v134
    ;;
  help|--help|-h)
    show_help_v134
    ;;
  *)
    exec python "$CORE" "$@"
    ;;
esac
