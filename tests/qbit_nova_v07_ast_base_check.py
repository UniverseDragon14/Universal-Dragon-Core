#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "engine" / "qbit_nova_v07_engine.py"
ZERO = ROOT / "examples" / "v2" / "qbit_nova_v07_native_zero.ud"

r = subprocess.run(
    [sys.executable, str(ENGINE), "ast", str(ZERO)],
    cwd=ROOT,
    text=True,
    capture_output=True,
)

out = (r.stdout or "") + (r.stderr or "")

if r.returncode != 0:
    print(out)
    raise SystemExit(r.returncode)

required = [
    '"language": "QBIT NOVA"',
    '"ud": "Universal Dragon"',
    '"creator": "Aslam"',
    '"team": "Askutty"',
    '"brain": "NovaKutty"',
    '"name": "player"',
    '"value": "Aslam"',
    '"name": "dragon"',
    '"state": "|0>"',
    '"target": "dragon"',
    '"QBIT NOVA v0.7 native engine online"',
    '"native_qvm"',
]

for item in required:
    if item not in out:
        print("MISSING:", item)
        print(out)
        raise SystemExit(1)

print("QBIT_NOVA_V07_AST_BASE_GREEN")
