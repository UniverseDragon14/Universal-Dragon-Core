#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PIPE = ROOT / "engine" / "qbit_nova_v08_pipeline.py"
ZERO = ROOT / "examples" / "v2" / "qbit_nova_v07_native_zero.ud"
ONE = ROOT / "examples" / "v2" / "qbit_nova_v07_native_one.ud"

def run_file(path):
    r = subprocess.run(
        [sys.executable, str(PIPE), str(path)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    out = (r.stdout or "") + (r.stderr or "")
    if r.returncode != 0:
        print(out)
        raise SystemExit(r.returncode)
    return out

zero = run_file(ZERO)
one = run_file(ONE)

checks = {
    "ZERO": [
        "QBIT NOVA v0.8 pipeline online",
        "pipeline: UD_SOURCE -> TOKENS -> AST -> QBIT_IR -> QVM",
        "TOKENS_BEGIN",
        "AST_BEGIN",
        "SEMANTIC_GREEN",
        "QBIT_IR_BEGIN",
        "QVM_RUN_BEGIN",
        "measure dragon => 0",
        "when dragon == 0 selected",
        "native safe branch selected",
        "QBIT_NOVA_V08_PIPELINE_GREEN",
    ],
    "ONE": [
        "measure dragon => 1",
        "when dragon == 1 selected",
        "native owner branch selected",
        "QBIT_NOVA_V08_PIPELINE_GREEN",
    ],
}

for item in checks["ZERO"]:
    if item not in zero:
        print("ZERO missing:", item)
        print(zero)
        raise SystemExit(1)

for item in checks["ONE"]:
    if item not in one:
        print("ONE missing:", item)
        print(one)
        raise SystemExit(1)

print("QBIT_NOVA_V08_PIPELINE_CONTRACT_GREEN")
