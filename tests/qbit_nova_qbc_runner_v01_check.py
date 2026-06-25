#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
SRC = ROOT / "examples" / "v2" / "qbit_nova_qbc_runner_contract_v01.qnova"
DOC = ROOT / "docs" / "QBIT_NOVA_QBC_RUNNER_V0_1.md"

if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import qbit_nova_qbc_runner_v01 as runner_tool

for p in [
    TOOLS / "qbit_nova_tokenizer_v01.py",
    TOOLS / "qbit_nova_parser_v01.py",
    TOOLS / "qbit_nova_ast_v01.py",
    TOOLS / "qbit_nova_ir_v01.py",
    TOOLS / "qbit_nova_qbc_v01.py",
    TOOLS / "qbit_nova_qbc_runner_v01.py",
    SRC,
    DOC,
]:
    if not p.exists():
        raise SystemExit(f"MISSING: {p}")

result = runner_tool.run_source(SRC.read_text(encoding="utf-8"))

if result.get("marker") != "QBIT_NOVA_QBC_RUNNER_V01":
    raise SystemExit("MISSING RUNNER MARKER")

if result.get("type") != "QBCRun":
    raise SystemExit("ROOT IS NOT QBCRun")

if result.get("mode") != "SAFE_BYTECODE_SIMULATION":
    raise SystemExit("RUNNER IS NOT SAFE_BYTECODE_SIMULATION")

if result.get("success") is not True:
    raise SystemExit("RUNNER SUCCESS NOT TRUE")

state = result.get("state", {})
trace = result.get("trace", [])

if state.get("meta", {}).get("creator") != "aslam":
    raise SystemExit("MISSING CREATOR META")

if state.get("meta", {}).get("project") != "universal_dragon":
    raise SystemExit("MISSING PROJECT META")

if state.get("meta", {}).get("brain") != "novakutty":
    raise SystemExit("MISSING BRAIN META")

if state.get("qbits", {}).get("intent") != "safe_patch":
    raise SystemExit("MISSING QBIT intent=safe_patch")

if "qbit_nova_identity_only" not in state.get("laws", []):
    raise SystemExit("MISSING LAW qbit_nova_identity_only")

if result.get("output") != "QBIT_NOVA_QBC_RUNNER_V01":
    raise SystemExit("MISSING RUNNER OUTPUT")

ops = [t.get("op") for t in trace]
opcodes = [t.get("opcode") for t in trace]

for op in [
    "PROGRAM.START",
    "META.SET",
    "LAW.SET",
    "QBIT.DEFINE",
    "GUARD.START",
    "ACTION.CHECK",
    "ACTION.BACKUP",
    "ACTION.VALIDATE",
    "ACTION.ROLLBACK",
    "ACTION.LEARN",
    "GUARD.END",
    "EMIT",
    "PROGRAM.END",
]:
    if op not in ops:
        raise SystemExit(f"MISSING RUNNER OP: {op}")

for opcode in ["01", "02", "10", "11", "20", "30", "31", "32", "33", "34", "35", "36", "40"]:
    if opcode not in opcodes:
        raise SystemExit(f"MISSING RUNNER OPCODE: {opcode}")

doc = DOC.read_text(encoding="utf-8")
for marker in [
    "QBIT NOVA QBC Runner v0.1",
    "SAFE BYTECODE SIMULATION",
    "QBIT_NOVA_QBC_RUNNER_V01",
]:
    if marker not in doc:
        raise SystemExit(f"MISSING DOC MARKER: {marker}")

print("QBIT_NOVA_QBC_RUNNER_V01_GREEN")
