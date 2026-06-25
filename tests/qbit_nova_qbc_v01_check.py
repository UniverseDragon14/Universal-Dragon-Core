#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
SRC = ROOT / "examples" / "v2" / "qbit_nova_qbc_contract_v01.qnova"
DOC = ROOT / "docs" / "QBIT_NOVA_QBC_V0_1.md"

if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import qbit_nova_qbc_v01 as qbc_tool

for p in [
    TOOLS / "qbit_nova_tokenizer_v01.py",
    TOOLS / "qbit_nova_parser_v01.py",
    TOOLS / "qbit_nova_ast_v01.py",
    TOOLS / "qbit_nova_ir_v01.py",
    TOOLS / "qbit_nova_qbc_v01.py",
    SRC,
    DOC,
]:
    if not p.exists():
        raise SystemExit(f"MISSING: {p}")

qbc = qbc_tool.build_qbc(SRC.read_text(encoding="utf-8"))

if qbc.get("marker") != "QBIT_NOVA_QBC_V01":
    raise SystemExit("MISSING QBC MARKER")

if qbc.get("type") != "QBCProgram":
    raise SystemExit("ROOT IS NOT QBCProgram")

if qbc.get("format") != "QBC_SYMBOLIC_V01":
    raise SystemExit("BAD QBC FORMAT")

ops = [i.get("op") for i in qbc.get("bytecode", [])]
opcodes = [i.get("opcode") for i in qbc.get("bytecode", [])]
pool = qbc.get("arg_pool", [])
stream = qbc.get("compact_stream", [])

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
        raise SystemExit(f"MISSING QBC OP: {op}")

required_opcodes = ["01", "02", "10", "11", "20", "30", "31", "32", "33", "34", "35", "36", "40"]

for code in required_opcodes:
    if code not in opcodes:
        raise SystemExit(f"MISSING QBC OPCODE: {code}")

for value in [
    "aslam",
    "universal_dragon",
    "novakutty",
    "safe_patch",
    "first",
    "before_change",
    "after_change",
    "on_fail",
    "always",
    "QBIT_NOVA_QBC_V01",
]:
    if value not in pool:
        raise SystemExit(f"MISSING QBC POOL VALUE: {value}")

if len(stream) <= len(opcodes):
    raise SystemExit("COMPACT STREAM TOO SMALL")

doc = DOC.read_text(encoding="utf-8")
for marker in [
    "QBIT NOVA QBC v0.1",
    "QBC means QBIT Bytecode",
    "QBIT_NOVA_QBC_V01",
]:
    if marker not in doc:
        raise SystemExit(f"MISSING DOC MARKER: {marker}")

print("QBIT_NOVA_QBC_V01_GREEN")
