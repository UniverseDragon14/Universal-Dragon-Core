#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import qbit_nova_ast_v01 as qast_tool


class QIRBuilder:
    def __init__(self):
        self.count = 0
        self.instructions = []

    def next_id(self):
        self.count += 1
        return f"QI{self.count:04d}"

    def emit(self, op, args, node):
        inst = {
            "id": self.next_id(),
            "op": op,
            "args": list(args),
            "line": node.get("line", 0),
            "qpath": node.get("qpath", ""),
        }
        self.instructions.append(inst)
        return inst

    def build(self, qast):
        self.emit("PROGRAM.START", ["qbit_nova"], qast)

        for child in qast.get("children", []):
            self.walk(child)

        self.emit("PROGRAM.END", ["qbit_nova"], qast)

        return {
            "marker": "QBIT_NOVA_IR_V01",
            "type": "QIRProgram",
            "instruction_count": len(self.instructions),
            "instructions": self.instructions,
        }

    def walk(self, node):
        ntype = node.get("type", "QASTStatement")
        head = str(node.get("head", ""))
        values = node.get("values", [])
        args = values[1:] if len(values) > 1 else []

        if ntype == "QASTHeader":
            self.emit("META.SET", [head] + args, node)
            return

        if ntype == "QASTLaw":
            self.emit("LAW.SET", args, node)
            return

        if ntype == "QASTQbit":
            clean = [v for v in args if v != "="]
            self.emit("QBIT.DEFINE", clean, node)
            return

        if ntype == "QASTGuard":
            guard_name = args[0] if args else head
            self.emit("GUARD.START", [guard_name], node)

            for child in node.get("children", []):
                self.walk(child)

            self.emit("GUARD.END", [guard_name], node)
            return

        if ntype == "QASTAction":
            op = "ACTION." + head.upper()
            self.emit(op, args, node)
            return

        if ntype == "QASTEmit":
            self.emit("EMIT", args, node)
            return

        self.emit("STATEMENT", values, node)

        for child in node.get("children", []):
            self.walk(child)


def build_ir(source: str):
    qast = qast_tool.build_qast(source)
    return QIRBuilder().build(qast)


def main(argv):
    if len(argv) != 2:
        print("Usage: qbit_nova_ir_v01.py <file.qnova|file.ud>")
        return 2

    path = Path(argv[1])
    if not path.exists():
        print(f"File not found: {path}")
        return 1

    qir = build_ir(path.read_text(encoding="utf-8"))

    print("QBIT_NOVA_IR_V01")
    print(json.dumps(qir, indent=2, ensure_ascii=False))
    print("QBIT_NOVA_IR_V01_GREEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
