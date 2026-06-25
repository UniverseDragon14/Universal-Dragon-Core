#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
SRC = ROOT / "examples" / "v2" / "qbit_nova_ast_contract_v01.qnova"
DOC = ROOT / "docs" / "QBIT_NOVA_AST_V0_1.md"

if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import qbit_nova_ast_v01 as qast_tool

for p in [
    TOOLS / "qbit_nova_tokenizer_v01.py",
    TOOLS / "qbit_nova_parser_v01.py",
    TOOLS / "qbit_nova_ast_v01.py",
    SRC,
    DOC,
]:
    if not p.exists():
        raise SystemExit(f"MISSING: {p}")

qast = qast_tool.build_qast(SRC.read_text(encoding="utf-8"))

if qast.get("marker") != "QBIT_NOVA_AST_V01":
    raise SystemExit("MISSING QAST MARKER")

if qast.get("type") != "QASTProgram":
    raise SystemExit("ROOT IS NOT QASTProgram")

types = []
values = []

def walk(node):
    if isinstance(node, dict):
        if "type" in node:
            types.append(node["type"])
        for v in node.get("values", []):
            values.append(v)
        for child in node.get("children", []):
            walk(child)

walk(qast)

required_types = [
    "QASTProgram",
    "QASTHeader",
    "QASTLaw",
    "QASTQbit",
    "QASTGuard",
    "QASTAction",
    "QASTEmit",
]

for t in required_types:
    if t not in types:
        raise SystemExit(f"MISSING QAST TYPE: {t}")

required_values = [
    "qnova",
    "creator",
    "aslam",
    "project",
    "universal_dragon",
    "brain",
    "novakutty",
    "qbit",
    "intent",
    "guard",
    "check",
    "backup",
    "validate",
    "rollback",
    "learn",
    "emit",
    "QBIT_NOVA_AST_V01",
]

for v in required_values:
    if v not in values:
        raise SystemExit(f"MISSING QAST VALUE: {v}")

doc = DOC.read_text(encoding="utf-8")
for marker in [
    "QBIT NOVA AST v0.1",
    "AST means Abstract Syntax Tree",
    "QBIT_NOVA_AST_V01",
]:
    if marker not in doc:
        raise SystemExit(f"MISSING DOC MARKER: {marker}")

print("QBIT_NOVA_AST_V01_GREEN")
