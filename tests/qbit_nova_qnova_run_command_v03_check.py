#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
DOC = ROOT / "docs" / "QBIT_NOVA_QNOVA_RUN_COMMAND_V0_3.md"
QNOVA = TOOLS / "qnova"
SRC = ROOT / "examples" / "v2" / "qbit_nova_qbc_file_runner_v03.qnova"
OUT = ROOT / ".tmp" / "qnova-run-v03" / "qbit_nova_qnova_run_command_v03.qbc"

for p in [
    DOC,
    QNOVA,
    TOOLS / "qbit_nova_qbc_file_runner_v03.py",
    TOOLS / "qbit_nova_qbc_file_writer_v03.py",
    TOOLS / "qbit_nova_qbc_file_loader_v03.py",
    SRC,
]:
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
    raise SystemExit("QNOVA RUN COMMAND FAILED")

if "QBIT_NOVA_QNOVA_RUN_COMMAND_V03_GREEN" not in result.stdout:
    print(result.stdout)
    raise SystemExit("MISSING QNOVA RUN GREEN MARKER")

if "QBIT_NOVA_QBC_FILE_RUNNER_V03" not in result.stdout:
    print(result.stdout)
    raise SystemExit("MISSING QBC FILE RUNNER MARKER")

if not OUT.exists():
    raise SystemExit(f"MISSING OUTPUT QBC: {OUT}")

qbc_text = OUT.read_text(encoding="utf-8")
if "FF" in qbc_text.split():
    raise SystemExit("UNKNOWN OPCODE FF FOUND")

for suffix in [".json", ".pool.json", ".expanded.qnova"]:
    p = Path(str(OUT) + suffix)
    if not p.exists():
        raise SystemExit(f"MISSING OUTPUT SIDE FILE: {p}")
    if p.stat().st_size <= 0:
        raise SystemExit(f"EMPTY OUTPUT SIDE FILE: {p}")

doc = DOC.read_text(encoding="utf-8")
for marker in [
    "QBIT_NOVA_QNOVA_RUN_COMMAND_V03",
    "Python is still used internally as a bootstrap construction tool",
    "Project language: QBIT NOVA",
    "Bytecode: QBC",
    "./tools/qnova run source.qnova",
    "SAFE QNOVA RUN COMMAND",
]:
    if marker not in doc:
        raise SystemExit(f"MISSING DOC MARKER: {marker}")

print("QBIT_NOVA_QNOVA_RUN_COMMAND_V03_GREEN")
