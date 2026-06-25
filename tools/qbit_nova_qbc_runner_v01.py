#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import qbit_nova_qbc_v01 as qbc_tool


OPCODE_TO_OP = {v: k for k, v in qbc_tool.OPCODES.items()}
OPCODE_TO_OP["FF"] = "UNKNOWN"


class QBCRunner:
    def __init__(self):
        self.state = {
            "meta": {},
            "laws": [],
            "qbits": {},
            "guards": [],
            "actions": [],
            "output": None,
        }
        self.trace = []

    def decode_args(self, indexes, pool):
        out = []
        for index in indexes:
            if isinstance(index, int) and 0 <= index < len(pool):
                out.append(pool[index])
            else:
                out.append(f"<BAD_ARG:{index}>")
        return out

    def step(self, item, pool):
        opcode = item.get("opcode", "FF")
        op = OPCODE_TO_OP.get(opcode, "UNKNOWN")
        args = self.decode_args(item.get("args", []), pool)

        entry = {
            "opcode": opcode,
            "op": op,
            "args": args,
            "line": item.get("line", 0),
            "qpath": item.get("qpath", ""),
            "status": "SAFE_BYTECODE_SIMULATION",
        }

        if op == "PROGRAM.START":
            entry["message"] = "bytecode program started"

        elif op == "PROGRAM.END":
            entry["message"] = "bytecode program ended"

        elif op == "META.SET":
            if args:
                self.state["meta"][args[0]] = " ".join(args[1:])
            entry["message"] = "metadata decoded"

        elif op == "LAW.SET":
            self.state["laws"].append(".".join(args))
            entry["message"] = "law decoded"

        elif op == "QBIT.DEFINE":
            if len(args) >= 2:
                self.state["qbits"][args[0]] = args[-1]
            entry["message"] = "qbit decoded"

        elif op == "GUARD.START":
            guard = args[0] if args else "unknown"
            self.state["guards"].append({"name": guard, "status": "active"})
            entry["message"] = "guard decoded"

        elif op == "GUARD.END":
            entry["message"] = "guard closed"

        elif op.startswith("ACTION."):
            action = {
                "name": op.replace("ACTION.", "").lower(),
                "args": args,
                "mode": "bytecode_simulation",
            }
            self.state["actions"].append(action)
            entry["message"] = f"action decoded: {action['name']}"

        elif op == "EMIT":
            self.state["output"] = " ".join(args)
            entry["message"] = "output decoded"

        else:
            entry["status"] = "UNKNOWN_OPCODE"
            entry["message"] = "unknown opcode preserved"

        self.trace.append(entry)

    def run(self, qbc):
        pool = qbc.get("arg_pool", [])

        for item in qbc.get("bytecode", []):
            self.step(item, pool)

        return {
            "marker": "QBIT_NOVA_QBC_RUNNER_V01",
            "type": "QBCRun",
            "mode": "SAFE_BYTECODE_SIMULATION",
            "success": True,
            "state": self.state,
            "trace": self.trace,
            "output": self.state["output"],
        }


def run_source(source: str):
    qbc = qbc_tool.build_qbc(source)
    return QBCRunner().run(qbc)


def main(argv):
    if len(argv) != 2:
        print("Usage: qbit_nova_qbc_runner_v01.py <file.qnova|file.ud>")
        return 2

    path = Path(argv[1])
    if not path.exists():
        print(f"File not found: {path}")
        return 1

    result = run_source(path.read_text(encoding="utf-8"))

    print("QBIT_NOVA_QBC_RUNNER_V01")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("QBIT_NOVA_QBC_RUNNER_V01_GREEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
