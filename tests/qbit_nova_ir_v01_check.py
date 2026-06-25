#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
SRC = ROOT / "examples" / "v2" / "qbit_nova_ir_contract_v01.qnova"
DOC = ROOT / "docs" / "QBIT_NOVA_IR_V0_1.md"

if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import qbit_nova_ir_v01 as qir_tool

for p in [
    TOOLS / "qbit_nova_tokenizer_v01.py",
    TOOLS / "qbit_nova_parser_v01.py",
    TOOLS / "qbit_nova_ast_v01.py",
    TOOLS / "qbit_nova_ir_v01.py",
    SRC,
    DOC,
]:
    if not p.exists():
        raise SystemExit(f"MISSING: {p}")

qir = qir_tool.build_ir(SRC.read_text(encoding="utf-8"))

if qir.get("marker") != "QBIT_NOVA_IR_V01":
    raise SystemExit("MISSING QIR MARKER")

if qir.get("type") != "QIRProgram":
    raise SystemExit("ROOT IS NOT QIRProgram")

instructions = qir.get("instructions", [])
ops = [i.get("op") for i in instructions]
args_blob = " ".join(" ".join(i.get("args", [])) for i in instructions)

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
        raise SystemExit(f"MISSING QIR OP: {op}")

required_args = [
    "aslam",
    "universal_dragon",
    "novakutty",
    "intent",
    "safe_patch",
    "first",
    "before_change",
    "after_change",
    "on_fail",
    "always",
    "QBIT_NOVA_IR_V01",
]

for arg in required_args:
    if arg not in args_blob:
        raise SystemExit(f"MISSING QIR ARG: {arg}")

doc = DOC.read_text(encoding="utf-8")
for marker in [
    "QBIT NOVA IR v0.1",
    "IR means Intermediate Representation",
    "QBIT_NOVA_IR_V01",
]:
    if marker not in doc:
        raise SystemExit(f"MISSING DOC MARKER: {marker}")

print("QBIT_NOVA_IR_V01_GREEN")
