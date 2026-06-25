#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
SRC = ROOT / "examples" / "v2" / "qbit_nova_dna_v01.qnova"
DOC = ROOT / "docs" / "QBIT_NOVA_PARSER_V0_1.md"

if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import qbit_nova_parser_v01 as parser

for p in [
    TOOLS / "qbit_nova_tokenizer_v01.py",
    TOOLS / "qbit_nova_parser_v01.py",
    SRC,
    DOC,
]:
    if not p.exists():
        raise SystemExit(f"MISSING: {p}")

ast = parser.parse_source(SRC.read_text(encoding="utf-8"))

if ast.get("marker") != "QBIT_NOVA_PARSER_V01":
    raise SystemExit("MISSING AST MARKER")

if ast.get("type") != "Program":
    raise SystemExit("AST root is not Program")

body = ast.get("body", [])

types = []
values = []

def walk(node):
    if isinstance(node, dict):
        if "type" in node:
            types.append(node["type"])
        for term in node.get("terms", []):
            values.append(term.get("value"))
        for term in node.get("header", []):
            values.append(term.get("value"))
        for child in node.get("body", []):
            walk(child)

for node in body:
    walk(node)

required_types = [
    "HeaderStatement",
    "LawStatement",
    "QbitStatement",
    "GuardBlock",
    "EmitStatement",
]

for t in required_types:
    if t not in types:
        raise SystemExit(f"MISSING AST TYPE: {t}")

required_values = [
    "qnova",
    "identity",
    "novakutty",
    "creator",
    "aslam",
    "law",
    "no_existing_language_identity",
    "guard",
    "intent",
    "rollback",
    "on_fail",
    "emit",
    "QBIT_NOVA_LANGUAGE_DNA_V01",
]

for v in required_values:
    if v not in values:
        raise SystemExit(f"MISSING AST VALUE: {v}")

doc = DOC.read_text(encoding="utf-8")
for marker in [
    "QBIT NOVA Parser v0.1",
    "Existing host tools are bootstrap construction tools only",
    "QBIT_NOVA_PARSER_V01",
]:
    if marker not in doc:
        raise SystemExit(f"MISSING DOC MARKER: {marker}")

print("QBIT_NOVA_PARSER_V01_GREEN")
