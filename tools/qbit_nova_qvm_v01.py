#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import qbit_nova_ir_v01 as qir_tool


class QVM:
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

    def step(self, inst):
        op = inst.get("op", "")
        args = inst.get("args", [])
        line = inst.get("line", 0)
        qpath = inst.get("qpath", "")

        entry = {
            "op": op,
            "args": args,
            "line": line,
            "qpath": qpath,
            "status": "SAFE_SIMULATION",
        }

        if op == "PROGRAM.START":
            entry["message"] = "QVM program started"

        elif op == "PROGRAM.END":
            entry["message"] = "QVM program ended"

        elif op == "META.SET":
            if args:
                key = args[0]
                value = " ".join(args[1:]) if len(args) > 1 else ""
                self.state["meta"][key] = value
            entry["message"] = "metadata stored"

        elif op == "LAW.SET":
            law = ".".join(args) if args else ""
            self.state["laws"].append(law)
            entry["message"] = "law stored"

        elif op == "QBIT.DEFINE":
            if len(args) >= 2:
                self.state["qbits"][args[0]] = args[-1]
            entry["message"] = "qbit meaning stored"

        elif op == "GUARD.START":
            guard = args[0] if args else "unknown"
            self.state["guards"].append({
                "name": guard,
                "status": "active",
            })
            entry["message"] = "guardian block opened"

        elif op == "GUARD.END":
            guard = args[0] if args else "unknown"
            entry["message"] = f"guardian block closed: {guard}"

        elif op.startswith("ACTION."):
            action = {
                "name": op.replace("ACTION.", "").lower(),
                "args": args,
                "mode": "simulation",
            }
            self.state["actions"].append(action)
            entry["message"] = f"action simulated: {action['name']}"

        elif op == "EMIT":
            self.state["output"] = " ".join(args)
            entry["message"] = "output emitted"

        else:
            entry["status"] = "UNKNOWN_OP"
            entry["message"] = "unknown op preserved"

        self.trace.append(entry)

    def run(self, qir):
        for inst in qir.get("instructions", []):
            self.step(inst)

        return {
            "marker": "QBIT_NOVA_QVM_V01",
            "type": "QVMRun",
            "mode": "SAFE_SIMULATION",
            "success": True,
            "state": self.state,
            "trace": self.trace,
            "output": self.state["output"],
        }


def run_source(source: str):
    qir = qir_tool.build_ir(source)
    return QVM().run(qir)


def main(argv):
    if len(argv) != 2:
        print("Usage: qbit_nova_qvm_v01.py <file.qnova|file.ud>")
        return 2

    path = Path(argv[1])
    if not path.exists():
        print(f"File not found: {path}")
        return 1

    result = run_source(path.read_text(encoding="utf-8"))

    print("QBIT_NOVA_QVM_V01")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("QBIT_NOVA_QVM_V01_GREEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
