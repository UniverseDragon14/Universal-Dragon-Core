#!/usr/bin/env python3
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
SRC = ROOT / "examples" / "v2" / "qbit_nova_qbc_file_writer_v03.qnova"
DOC = ROOT / "docs" / "QBIT_NOVA_QBC_FILE_WRITER_V0_3.md"
OUT = ROOT / ".tmp" / "qbc-v03" / "qbit_nova_qbc_file_writer_v03.qbc"

if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import qbit_nova_qbc_file_writer_v03 as writer

for p in [
    TOOLS / "qbit_nova_syntax_v02.py",
    TOOLS / "qbit_nova_qbc_v01.py",
    TOOLS / "qbit_nova_qbc_file_writer_v03.py",
    SRC,
    DOC,
]:
    if not p.exists():
        raise SystemExit(f"MISSING: {p}")

result = writer.write_qbc_file(SRC, OUT)

if result.get("marker") != "QBIT_NOVA_QBC_FILE_WRITER_V03":
    raise SystemExit("MISSING WRITER MARKER")

if result.get("mode") != "SAFE_BYTECODE_FILE_WRITE":
    raise SystemExit("BAD WRITER MODE")

if result.get("success") is not True:
    raise SystemExit("WRITER SUCCESS NOT TRUE")

for key in ["qbc", "json", "pool", "expanded"]:
    p = Path(result[key])
    if not p.exists():
        raise SystemExit(f"MISSING OUTPUT FILE: {p}")
    if p.stat().st_size <= 0:
        raise SystemExit(f"EMPTY OUTPUT FILE: {p}")

qbc_text = Path(result["qbc"]).read_text(encoding="utf-8")
for opcode in ["01", "10", "11", "20", "30", "31", "32", "33", "34", "35", "36", "40", "02"]:
    if opcode not in qbc_text.split():
        raise SystemExit(f"MISSING OPCODE IN QBC FILE: {opcode}")

qbc_json = json.loads(Path(result["json"]).read_text(encoding="utf-8"))
if qbc_json.get("marker") != "QBIT_NOVA_QBC_V01":
    raise SystemExit("BAD QBC JSON MARKER")

pool = json.loads(Path(result["pool"]).read_text(encoding="utf-8"))
for value in ["aslam", "novakutty", "universal_dragon", "qbc_file_writer", "QBIT_NOVA_QBC_FILE_WRITER_V03"]:
    if value not in pool:
        raise SystemExit(f"MISSING POOL VALUE: {value}")

doc = DOC.read_text(encoding="utf-8")
for marker in [
    "QBIT NOVA QBC File Writer v0.3",
    "real `.qbc` file",
    "QBIT_NOVA_QBC_FILE_WRITER_V03",
]:
    if marker not in doc:
        raise SystemExit(f"MISSING DOC MARKER: {marker}")

print("QBIT_NOVA_QBC_FILE_WRITER_V03_GREEN")
