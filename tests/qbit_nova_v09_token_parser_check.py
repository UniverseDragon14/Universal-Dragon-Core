#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PARSER = ROOT / "engine" / "qbit_nova_v09_token_parser.py"
ZERO = ROOT / "examples" / "v2" / "qbit_nova_v07_native_zero.ud"
ONE = ROOT / "examples" / "v2" / "qbit_nova_v07_native_one.ud"

def run_parser(src):
    r = subprocess.run(
        [sys.executable, str(PARSER), str(src)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    out = (r.stdout or "") + (r.stderr or "")
    if r.returncode != 0:
        print(out)
        raise SystemExit(r.returncode)
    return out

zero = run_parser(ZERO)
one = run_parser(ONE)

zero_required = [
    "QBIT NOVA v0.9 token parser online",
    '"language": "QBIT NOVA"',
    '"version": "v0.9-token-parser"',
    '"ud": "Universal Dragon"',
    '"creator": "Aslam"',
    '"team": "Askutty"',
    '"brain": "NovaKutty"',
    '"parser": "token_stream"',
    '"name": "player"',
    '"value": "Aslam"',
    '"name": "dragon"',
    '"state": "|0>"',
    '"target": "dragon"',
    '"condition": "dragon == 0"',
    '"say native safe branch selected"',
    '"condition": "dragon == 1"',
    '"say native owner branch selected"',
    '"name": "whatsapp"',
    '"mode safe_reply"',
    '"owner_approval required"',
    '"risky_action deny"',
    '"native_qvm"',
    "QBIT_NOVA_V09_TOKEN_PARSER_GREEN",
]

one_required = [
    '"state": "|1>"',
    '"condition": "dragon == 1"',
    "QBIT_NOVA_V09_TOKEN_PARSER_GREEN",
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

print("QBIT_NOVA_V09_TOKEN_PARSER_CONTRACT_GREEN")
