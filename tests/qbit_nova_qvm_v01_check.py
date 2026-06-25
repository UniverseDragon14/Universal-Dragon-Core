#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
SRC = ROOT / "examples" / "v2" / "qbit_nova_qvm_contract_v01.qnova"
DOC = ROOT / "docs" / "QBIT_NOVA_QVM_V0_1.md"

if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import qbit_nova_qvm_v01 as qvm_tool

for p in [
    TOOLS / "qbit_nova_tokenizer_v01.py",
    TOOLS / "qbit_nova_parser_v01.py",
    TOOLS / "qbit_nova_ast_v01.py",
    TOOLS / "qbit_nova_ir_v01.py",
    TOOLS / "qbit_nova_qvm_v01.py",
    SRC,
    DOC,
]:
    if not p.exists():
        raise SystemExit(f"MISSING: {p}")

result = qvm_tool.run_source(SRC.read_text(encoding="utf-8"))

if result.get("marker") != "QBIT_NOVA_QVM_V01":
    raise SystemExit("MISSING QVM MARKER")

if result.get("type") != "QVMRun":
    raise SystemExit("ROOT IS NOT QVMRun")

if result.get("mode") != "SAFE_SIMULATION":
    raise SystemExit("QVM IS NOT SAFE_SIMULATION")

if result.get("success") is not True:
    raise SystemExit("QVM SUCCESS NOT TRUE")

state = result.get("state", {})
trace = result.get("trace", [])

if state.get("meta", {}).get("creator") != "aslam":
    raise SystemExit("MISSING CREATOR META")

if state.get("meta", {}).get("project") != "universal_dragon":
    raise SystemExit("MISSING PROJECT META")

if state.get("qbits", {}).get("intent") != "safe_patch":
    raise SystemExit("MISSING QBIT intent=safe_patch")

if "qbit_nova_identity_only" not in state.get("laws", []):
    raise SystemExit("MISSING LAW qbit_nova_identity_only")

if result.get("output") != "QBIT_NOVA_QVM_V01":
    raise SystemExit("MISSING QVM OUTPUT")

ops = [t.get("op") for t in trace]

required_ops = [
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
]

for op in required_ops:
    if op not in ops:
        raise SystemExit(f"MISSING QVM TRACE OP: {op}")

doc = DOC.read_text(encoding="utf-8")
for marker in [
    "QBIT NOVA QVM v0.1",
    "QVM means QBIT NOVA Virtual Machine",
    "SAFE SIMULATION",
    "QBIT_NOVA_QVM_V01",
]:
    if marker not in doc:
        raise SystemExit(f"MISSING DOC MARKER: {marker}")

print("QBIT_NOVA_QVM_V01_GREEN")
