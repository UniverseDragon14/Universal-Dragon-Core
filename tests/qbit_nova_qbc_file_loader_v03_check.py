#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
SRC = ROOT / "examples" / "v2" / "qbit_nova_qbc_file_loader_v03.qnova"
DOC = ROOT / "docs" / "QBIT_NOVA_QBC_FILE_LOADER_V0_3.md"
OUT = ROOT / ".tmp" / "qbc-v03-loader" / "qbit_nova_qbc_file_loader_v03.qbc"

if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import qbit_nova_qbc_file_writer_v03 as writer
import qbit_nova_qbc_file_loader_v03 as loader

for p in [
    TOOLS / "qbit_nova_qbc_file_writer_v03.py",
    TOOLS / "qbit_nova_qbc_file_loader_v03.py",
    TOOLS / "qbit_nova_qbc_runner_v01.py",
    SRC,
    DOC,
]:
    if not p.exists():
        raise SystemExit(f"MISSING: {p}")

write_result = writer.write_qbc_file(SRC, OUT)

if write_result.get("marker") != "QBIT_NOVA_QBC_FILE_WRITER_V03":
    raise SystemExit("WRITER FAILED BEFORE LOADER TEST")

load_result = loader.load_qbc_files(OUT)

if load_result.get("marker") != "QBIT_NOVA_QBC_FILE_LOADER_V03":
    raise SystemExit("MISSING LOADER MARKER")

if load_result.get("mode") != "SAFE_BYTECODE_FILE_LOAD":
    raise SystemExit("BAD LOADER MODE")

if load_result.get("success") is not True:
    raise SystemExit("LOADER SUCCESS NOT TRUE")

if load_result.get("runner_marker") != "QBIT_NOVA_QBC_RUNNER_V01":
    raise SystemExit("RUNNER MARKER MISSING")

if load_result.get("runner_mode") != "SAFE_BYTECODE_SIMULATION":
    raise SystemExit("BAD RUNNER MODE")

if load_result.get("decoded_output") != "QBIT_NOVA_QBC_FILE_LOADER_V03":
    raise SystemExit("BAD DECODED OUTPUT")

if load_result.get("output") != "QBIT_NOVA_QBC_FILE_LOADER_V03":
    raise SystemExit("BAD LOADER OUTPUT")

state = load_result.get("state", {})

if state.get("meta", {}).get("creator") != "aslam":
    raise SystemExit("MISSING CREATOR META")

if state.get("qbits", {}).get("intent") != "qbc_file_loader":
    raise SystemExit("MISSING QBIT intent=qbc_file_loader")

ops = [t.get("op") for t in load_result.get("trace", [])]
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

qbc_text = OUT.read_text(encoding="utf-8")
if "FF" in qbc_text.split():
    raise SystemExit("UNKNOWN OPCODE FF FOUND")

doc = DOC.read_text(encoding="utf-8")
for marker in [
    "QBIT NOVA QBC File Loader v0.3",
    "SAFE BYTECODE FILE LOAD",
    "QBIT_NOVA_QBC_FILE_LOADER_V03",
]:
    if marker not in doc:
        raise SystemExit(f"MISSING DOC MARKER: {marker}")

print("QBIT_NOVA_QBC_FILE_LOADER_V03_GREEN")
