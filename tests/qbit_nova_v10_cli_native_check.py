#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "tools" / "nova_cli.ud"
SRC = ROOT / "examples" / "v2" / "qbit_nova_v07_native_zero.ud"

def run_cmd(*args):
    r = subprocess.run(
        [sys.executable, str(CLI), *args],
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
        "nova native <file.ud>",
        "nova tokens <file.ud>",
        "nova ast-native <file.ud>",
        "nova ir <file.ud>",
    ],
    "native": [
        "QBIT NOVA v1.0 CLI native command",
        "QBIT NOVA v0.9 token pipeline online",
        "QBIT_NOVA_V09_PIPELINE_GREEN",
    ],
    "tokens": [
        "QBIT NOVA v1.0 CLI tokens command",
        "QBIT NOVA v0.8 tokenizer online",
        "QBIT_NOVA_V08_TOKENIZER_GREEN",
    ],
    "ast_native": [
        "QBIT NOVA v1.0 CLI ast-native command",
        "QBIT NOVA v0.9 token parser online",
        "QBIT_NOVA_V09_TOKEN_PARSER_GREEN",
    ],
    "ir": [
        "QBIT NOVA v1.0 IR command",
        "QBIT_IR_BEGIN",
        "ID",
        "QBIT",
        "MEASURE",
        "BRANCH",
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

for name, required_items in checks.items():
    out = outputs[name]
    for item in required_items:
        if item not in out:
            print(f"{name} missing: {item}")
            print(out)
            raise SystemExit(1)

print("QBIT_NOVA_V10_CLI_NATIVE_CONTRACT_GREEN")
