#!/usr/bin/env bash
# eve run — execute a QBIT NOVA program (Aslam's quantum-level language).
# Sources: .qn .qnova .ud    Bytecode: .qbc    Mode: SAFE_BOOTSTRAP (no OS exec).

eve_cmd_run() {
  local src="${1:-}"
  if [ -z "$src" ]; then
    eve_err "usage: ./eve run <program.qn|.qnova|.ud>"
    return 2
  fi
  [ -f "$src" ] || eve_die "program not found: $src"
  eve_info "QBIT NOVA · running $(basename "$src")  ${C_DIM}(safe pipeline)${C_RESET}"
  # Prefer the polished qnova command (compile+run to .qbc); fall back to the
  # full in-memory pipeline runner if qnova is unavailable.
  if [ -f "$EVE_ROOT/tools/qnova" ]; then
    eve_pyrun tools/qnova run "$src"
  else
    eve_pyrun tools/qbit_nova_run_v01.py "$src"
  fi
}

eve_cmd_qbc() {
  # Inspect/summarise a program without running: tokens/ast/ir/qbc counts.
  local src="${1:-}"
  [ -n "$src" ] || { eve_err "usage: ./eve qbc <program.qnova|.ud>"; return 2; }
  [ -f "$src" ] || eve_die "program not found: $src"
  eve_pyrun tools/qbit_nova_run_v01.py "$src"
}
