#!/usr/bin/env python3
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
QNOVA = ROOT / "tools" / "qnova"
SRC = ROOT / "examples" / "v2" / "qbit_nova_install_v03.qn"
OUT = ROOT / ".tmp" / "qnova-run-v03" / "qbit_nova_install_v03_fix_check.qbc"

for p in [QNOVA, SRC]:
    if not p.exists():
        raise SystemExit(f"MISSING: {p}")

result = subprocess.run(
    [str(QNOVA), "run", str(SRC), str(OUT)],
    cwd=str(ROOT),
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
)

if result.returncode != 0:
    print(result.stdout)
    raise SystemExit("INSTALL.QN RUN FAILED")

checks = [
    "QBIT_NOVA_QNOVA_RUN_COMMAND_V03_GREEN",
    "QBIT_NOVA_INSTALL_QN_V03",
    "SAFE_QNOVA_RUN_COMMAND",
]

for c in checks:
    if c not in result.stdout:
        print(result.stdout)
        raise SystemExit(f"MISSING OUTPUT MARKER: {c}")

qbc_text = OUT.read_text(encoding="utf-8")
if "FF" in qbc_text.split():
    raise SystemExit("UNKNOWN OPCODE FF FOUND")

for suffix in [".json", ".pool.json", ".expanded.qnova"]:
    side = Path(str(OUT) + suffix)
    if not side.exists():
        raise SystemExit(f"MISSING SIDE FILE: {side}")
    if side.stat().st_size <= 0:
        raise SystemExit(f"EMPTY SIDE FILE: {side}")

print("QBIT_NOVA_INSTALL_QN_V03_GREEN")
