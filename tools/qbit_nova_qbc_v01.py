#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import qbit_nova_ir_v01 as qir_tool


OPCODES = {
    "PROGRAM.START": "01",
    "PROGRAM.END": "02",
    "META.SET": "10",
    "LAW.SET": "11",
    "QBIT.DEFINE": "20",
    "GUARD.START": "30",
    "ACTION.CHECK": "31",
    "ACTION.BACKUP": "32",
    "ACTION.VALIDATE": "33",
    "ACTION.ROLLBACK": "34",
    "ACTION.LEARN": "35",
    "GUARD.END": "36",
    "EMIT": "40",
}


class QBCBuilder:
    def __init__(self):
        self.pool = []
        self.pool_index = {}

    def intern(self, value):
        value = str(value)
        if value not in self.pool_index:
            self.pool_index[value] = len(self.pool)
            self.pool.append(value)
        return self.pool_index[value]

    def encode_instruction(self, inst):
        op = inst.get("op", "")
        opcode = OPCODES.get(op, "FF")
        arg_indexes = [self.intern(arg) for arg in inst.get("args", [])]

        return {
            "opcode": opcode,
            "op": op,
            "args": arg_indexes,
            "line": inst.get("line", 0),
            "qpath": inst.get("qpath", ""),
        }

    def build(self, qir):
        bytecode = [
            self.encode_instruction(inst)
            for inst in qir.get("instructions", [])
        ]

        compact_stream = []
        for item in bytecode:
            compact_stream.append(item["opcode"])
            compact_stream.extend(f"{i:02X}" for i in item["args"])

        return {
            "marker": "QBIT_NOVA_QBC_V01",
            "type": "QBCProgram",
            "format": "QBC_SYMBOLIC_V01",
            "instruction_count": len(bytecode),
            "arg_pool": self.pool,
            "bytecode": bytecode,
            "compact_stream": compact_stream,
        }


def build_qbc(source: str):
    qir = qir_tool.build_ir(source)
    return QBCBuilder().build(qir)


def main(argv):
    if len(argv) != 2:
        print("Usage: qbit_nova_qbc_v01.py <file.qnova|file.ud>")
        return 2

    path = Path(argv[1])
    if not path.exists():
        print(f"File not found: {path}")
        return 1

    qbc = build_qbc(path.read_text(encoding="utf-8"))

    print("QBIT_NOVA_QBC_V01")
    print(json.dumps(qbc, indent=2, ensure_ascii=False))
    print("QBIT_NOVA_QBC_V01_GREEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
