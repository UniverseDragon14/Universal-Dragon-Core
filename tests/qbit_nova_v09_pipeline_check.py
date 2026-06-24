#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PIPE = ROOT / "engine" / "qbit_nova_v09_pipeline.py"
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

zero_required = [
    "QBIT NOVA v0.9 token pipeline online",
    "pipeline: UD_SOURCE -> TOKENS -> TOKEN_PARSER_AST -> SEMANTIC -> QBIT_IR -> QVM",
    "TOKEN_PARSER_AST_BEGIN",
    "parser: token_stream",
    "creator: Aslam",
    "team: Askutty",
    "brain: NovaKutty",
    "SEMANTIC_GREEN",
    "QBIT_IR_BEGIN",
    "QVM_RUN_BEGIN",
    "qbit dragon = |0>",
    "measure dragon => 0",
    "when dragon == 0 selected",
    "native safe branch selected",
    "QBIT_NOVA_V09_PIPELINE_GREEN",
]

one_required = [
    "qbit dragon = |1>",
    "measure dragon => 1",
    "when dragon == 1 selected",
    "native owner branch selected",
    "QBIT_NOVA_V09_PIPELINE_GREEN",
]

for item in zero_required:
    if item not in zero:
        print("ZERO missing:", item)
        print(zero)
        raise SystemExit(1)

for item in one_required:
    if item not in one:
        print("ONE missing:", item)
        print(one)
        raise SystemExit(1)

print("QBIT_NOVA_V09_PIPELINE_CONTRACT_GREEN")
