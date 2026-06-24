#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ROOT / "tools" / "qbit-nova"
SRC = ROOT / "examples" / "v2" / "qbit_nova_v07_native_zero.ud"

def run_cmd(*args):
    r = subprocess.run(
        [str(LAUNCHER), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    out = (r.stdout or "") + (r.stderr or "")
    if r.returncode != 0:
        print(out)
        raise SystemExit(r.returncode)
    return out

doctor = run_cmd("doctor")
native = run_cmd("native", str(SRC))
tokens = run_cmd("tokens", str(SRC))
ast_native = run_cmd("ast-native", str(SRC))
ir = run_cmd("ir", str(SRC))

checks = {
    "doctor": [
        "QBIT NOVA doctor",
        "nova native <file.ud>",
        "nova tokens <file.ud>",
        "nova ast-native <file.ud>",
        "nova ir <file.ud>",
    ],
    "native": [
        "QBIT NOVA v1.0 CLI native command",
        "QBIT_NOVA_V09_PIPELINE_GREEN",
    ],
    "tokens": [
        "QBIT NOVA v1.0 CLI tokens command",
        "QBIT_NOVA_V08_TOKENIZER_GREEN",
    ],
    "ast_native": [
        "QBIT NOVA v1.0 CLI ast-native command",
        "QBIT_NOVA_V09_TOKEN_PARSER_GREEN",
    ],
    "ir": [
        "QBIT NOVA v1.0 IR command",
        "QBIT_IR_BEGIN",
        "QBIT_IR_END",
        "QBIT_NOVA_V10_IR_GREEN",
    ],
}

outputs = {
    "doctor": doctor,
    "native": native,
    "tokens": tokens,
    "ast_native": ast_native,
    "ir": ir,
}

for name, items in checks.items():
    out = outputs[name]
    for item in items:
        if item not in out:
            print(f"{name} missing: {item}")
            print(out)
            raise SystemExit(1)

print("QBIT_NOVA_V11_PORTABLE_LAUNCHER_GREEN")
