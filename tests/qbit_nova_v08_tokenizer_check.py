#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
TOK = ROOT / "engine" / "qbit_nova_v08_tokenizer.py"
SRC = ROOT / "examples" / "v2" / "qbit_nova_v07_native_zero.ud"

r = subprocess.run(
    [sys.executable, str(TOK), str(SRC)],
    cwd=ROOT,
    text=True,
    capture_output=True,
)

out = (r.stdout or "") + (r.stderr or "")

if r.returncode != 0:
    print(out)
    raise SystemExit(r.returncode)

required = [
    "QBIT NOVA v0.8 tokenizer online",
    '"type": "KEYWORD"',
    '"value": "nova"',
    '"value": "creator"',
    '"value": "Aslam"',
    '"value": "qbit"',
    '"type": "QSTATE"',
    '"value": "|0>"',
    '"value": "measure"',
    '"value": "when"',
    '"type": "INDENT"',
    '"type": "DEDENT"',
    '"value": "adapter"',
    '"value": "runtime"',
    "QBIT_NOVA_V08_TOKENIZER_GREEN",
]

for item in required:
    if item not in out:
        print("TOKENIZER missing:", item)
        print(out)
        raise SystemExit(1)

print("QBIT_NOVA_V08_TOKENIZER_CONTRACT_GREEN")
