#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import qbit_nova_parser_v01 as parser


class QASTBuilder:
    def __init__(self):
        self.count = 0

    def next_id(self):
        self.count += 1
        return f"QN{self.count:04d}"

    def build(self, parsed_ast):
        children = [self.convert(node, "root") for node in parsed_ast.get("body", [])]
        return {
            "marker": "QBIT_NOVA_AST_V01",
            "type": "QASTProgram",
            "id": "QN0000",
            "qpath": "program",
            "children": children,
            "summary": self.summary(children),
        }

    def convert(self, node, parent_path):
        base_type = node.get("type", "Statement")
        line = node.get("line", 0)

        terms = node.get("terms") or node.get("header") or []
        values = [t.get("value", "") for t in terms if t.get("value", "") != ""]
        head = values[0] if values else ""

        qtype = self.map_type(base_type, head, node)

        node_id = self.next_id()
        qpath = f"{parent_path}.{head or qtype.lower()}.{node_id}"

        children = [self.convert(child, qpath) for child in node.get("body", [])]

        return {
            "id": node_id,
            "type": qtype,
            "line": line,
            "head": head,
            "values": values,
            "qpath": qpath,
            "children": children,
        }

    def map_type(self, base_type, head, node):
        h = str(head).lower()

        if base_type == "GuardBlock" or h == "guard":
            return "QASTGuard"

        if h in ("qnova", "creator", "project", "brain", "team", "identity"):
            return "QASTHeader"

        if h == "law":
            return "QASTLaw"

        if h == "qbit":
            return "QASTQbit"

        if h == "emit":
            return "QASTEmit"

        if h in ("check", "backup", "validate", "rollback", "learn", "reply"):
            return "QASTAction"

        return "QASTStatement"

    def summary(self, children):
        found = []

        def walk(node):
            found.append(node.get("type"))
            for child in node.get("children", []):
                walk(child)

        for child in children:
            walk(child)

        return {
            "node_count": len(found),
            "types": sorted(set(found)),
        }


def build_qast(source: str):
    parsed = parser.parse_source(source)
    return QASTBuilder().build(parsed)


def main(argv):
    if len(argv) != 2:
        print("Usage: qbit_nova_ast_v01.py <file.qnova|file.ud>")
        return 2

    path = Path(argv[1])
    if not path.exists():
        print(f"File not found: {path}")
        return 1

    qast = build_qast(path.read_text(encoding="utf-8"))

    print("QBIT_NOVA_AST_V01")
    print(json.dumps(qast, indent=2, ensure_ascii=False))
    print("QBIT_NOVA_AST_V01_GREEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
