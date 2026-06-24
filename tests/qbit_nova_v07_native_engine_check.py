#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "engine" / "qbit_nova_v07_engine.py"
ZERO = ROOT / "examples" / "v2" / "qbit_nova_v07_native_zero.ud"
ONE = ROOT / "examples" / "v2" / "qbit_nova_v07_native_one.ud"

def run_cmd(args):
    r = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
    out = (r.stdout or "") + (r.stderr or "")
    if r.returncode != 0:
        print(out)
        raise SystemExit(r.returncode)
    return out

zero = run_cmd([sys.executable, str(ENGINE), "run", str(ZERO)])
one = run_cmd([sys.executable, str(ENGINE), "run", str(ONE)])
ast = run_cmd([sys.executable, str(ENGINE), "ast", str(ZERO)])
ir = run_cmd([sys.executable, str(ENGINE), "compile", str(ZERO)])
check = run_cmd([sys.executable, str(ENGINE), "check", str(ZERO)])

checks = {
    "ZERO": [
        "QBIT NOVA v0.7 native engine online",
        "compile path: UD_SOURCE -> AST -> QBIT_IR -> QVM",
        "QBIT_IR_BEGIN",
        "QBIT_IR_END",
        "QVM_RUN_BEGIN",
        "measure dragon => 0",
        "when dragon == 0 selected",
        "native safe branch selected",
        "adapter whatsapp contract loaded",
        "mode safe_reply",
        "owner_approval required",
        "risky_action deny",
        "QBIT_NOVA_V07_NATIVE_ENGINE_GREEN",
    ],
    "ONE": [
        "measure dragon => 1",
        "when dragon == 1 selected",
        "native owner branch selected",
        "QBIT_NOVA_V07_NATIVE_ENGINE_GREEN",
    ],
    "AST": [
        '"language": "QBIT NOVA"',
        '"ud": "Universal Dragon"',
        '"creator": "Aslam"',
        '"team": "Askutty"',
        '"brain": "NovaKutty"',
        '"name": "dragon"',
        '"state": "|0>"',
    ],
    "IR": [
        "ID\tLANGUAGE\tQBIT NOVA",
        "ID\tCREATOR\tAslam",
        "QBIT\tdragon\t|0>",
        "MEASURE\tdragon",
        "BRANCH\tdragon == 0",
        "ADAPTER\twhatsapp",
        "RUNTIME\tnative_qvm",
    ],
    "CHECK": [
        "semantic status: GREEN",
        "QBIT_NOVA_V07_SEMANTIC_GREEN",
    ],
}

outputs = {
    "ZERO": zero,
    "ONE": one,
    "AST": ast,
    "IR": ir,
    "CHECK": check,
}

for name, items in checks.items():
    for item in items:
        if item not in outputs[name]:
            print(name + " missing: " + item)
            print(outputs[name])
            raise SystemExit(1)

print("QBIT_NOVA_V07_NATIVE_ENGINE_CONTRACT_GREEN")
