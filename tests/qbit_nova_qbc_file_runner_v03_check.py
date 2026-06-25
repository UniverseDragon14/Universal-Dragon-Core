#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
SRC = ROOT / "examples" / "v2" / "qbit_nova_qbc_file_runner_v03.qnova"
DOC = ROOT / "docs" / "QBIT_NOVA_QBC_FILE_RUNNER_V0_3.md"
OUT = ROOT / ".tmp" / "qbc-v03-runner" / "qbit_nova_qbc_file_runner_v03.qbc"

if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import qbit_nova_qbc_file_runner_v03 as runner

for p in [
    TOOLS / "qbit_nova_qbc_file_writer_v03.py",
    TOOLS / "qbit_nova_qbc_file_loader_v03.py",
    TOOLS / "qbit_nova_qbc_file_runner_v03.py",
    TOOLS / "qbit_nova_qbc_runner_v01.py",
    SRC,
    DOC,
]:
    if not p.exists():
        raise SystemExit(f"MISSING: {p}")

result = runner.run_qbc_file(SRC, OUT)

if result.get("marker") != "QBIT_NOVA_QBC_FILE_RUNNER_V03":
    raise SystemExit("MISSING RUNNER MARKER")

if result.get("mode") != "SAFE_QBC_FILE_RUN":
    raise SystemExit("BAD RUNNER MODE")

if result.get("success") is not True:
    raise SystemExit("RUNNER SUCCESS NOT TRUE")

if result.get("writer_marker") != "QBIT_NOVA_QBC_FILE_WRITER_V03":
    raise SystemExit("WRITER MARKER MISSING")

if result.get("loader_marker") != "QBIT_NOVA_QBC_FILE_LOADER_V03":
    raise SystemExit("LOADER MARKER MISSING")

if result.get("runner_marker") != "QBIT_NOVA_QBC_RUNNER_V01":
    raise SystemExit("BYTECODE RUNNER MARKER MISSING")

if result.get("runner_mode") != "SAFE_BYTECODE_SIMULATION":
    raise SystemExit("BAD BYTECODE RUNNER MODE")

if result.get("decoded_output") != "QBIT_NOVA_QBC_FILE_RUNNER_V03":
    raise SystemExit("BAD DECODED OUTPUT")

if result.get("output") != "QBIT_NOVA_QBC_FILE_RUNNER_V03":
    raise SystemExit("BAD OUTPUT")

for key in ["qbc", "json", "pool", "expanded"]:
    p = Path(result[key])
    if not p.exists():
        raise SystemExit(f"MISSING OUTPUT FILE: {p}")
    if p.stat().st_size <= 0:
        raise SystemExit(f"EMPTY OUTPUT FILE: {p}")

qbc_text = OUT.read_text(encoding="utf-8")
if "FF" in qbc_text.split():
    raise SystemExit("UNKNOWN OPCODE FF FOUND")

state = result.get("state", {})

if state.get("meta", {}).get("creator") != "aslam":
    raise SystemExit("MISSING CREATOR META")

if state.get("qbits", {}).get("intent") != "qbc_file_runner":
    raise SystemExit("MISSING QBIT intent=qbc_file_runner")

ops = [t.get("op") for t in result.get("trace", [])]
for op in [
    "PROGRAM.START",
    "META.SET",
    "LAW.SET",
    "QBIT.DEFINE",
    "GUARD.START",
    "ACTION.CHECK",
    "ACTION.BACKUP",
    "ACTION.VALIDATE",
    "ACTION.ROLLBACK",
    "ACTION.LEARN",
    "GUARD.END",
    "EMIT",
    "PROGRAM.END",
]:
    if op not in ops:
        raise SystemExit(f"MISSING TRACE OP: {op}")

doc = DOC.read_text(encoding="utf-8")
for marker in [
    "QBIT NOVA QBC File Runner v0.3",
    "SAFE QBC FILE RUN",
    "source.qnova",
    "write output.qbc",
    "load output.qbc",
    "decode safe trace",
    "QBIT_NOVA_QBC_FILE_RUNNER_V03",
]:
    if marker not in doc:
        raise SystemExit(f"MISSING DOC MARKER: {marker}")

print("QBIT_NOVA_QBC_FILE_RUNNER_V03_GREEN")
