#!/usr/bin/env python3
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "QBIT_NOVA_QN_SOURCE_SPEC_V0_3.md"
QNOVA = ROOT / "tools" / "qnova"

QN_SRC = ROOT / "examples" / "v2" / "qbit_nova_install_v03.qn"
QN_OUT = ROOT / ".tmp" / "qn-source-spec-v03" / "install_spec_check.qbc"

QNOVA_SRC = ROOT / "examples" / "v2" / "qbit_nova_qbc_file_runner_v03.qnova"
QNOVA_OUT = ROOT / ".tmp" / "qn-source-spec-v03" / "runner_spec_check.qbc"

for p in [DOC, QNOVA, QN_SRC, QNOVA_SRC]:
    if not p.exists():
        raise SystemExit(f"MISSING: {p}")

doc = DOC.read_text(encoding="utf-8")

checks = [
    "QBIT_NOVA_QN_SOURCE_SPEC_V03",
    "`.qn` is the short QBIT NOVA source file extension",
    "`.qnova` is the long QBIT NOVA source file extension",
    "`.qbc` is QBIT NOVA compiled bytecode",
    "install.qn is safe manifest only",
    "Python files are bootstrap construction tools only",
    "Project language: QBIT NOVA",
    "./tools/qnova run source.qn",
    "./tools/qnova run source.qnova",
    "No business/dashboard mixing in this chat",
]

for c in checks:
    if c not in doc:
        raise SystemExit(f"MISSING DOC MARKER: {c}")

def run_source(src: Path, out: Path, expected_marker: str):
    result = subprocess.run(
        [str(QNOVA), "run", str(src), str(out)],
        cwd=str(ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    if result.returncode != 0:
        print(result.stdout)
        raise SystemExit(f"RUN FAILED: {src}")

    required = [
        "QBIT_NOVA_QNOVA_RUN_COMMAND_V03_GREEN",
        expected_marker,
        "SAFE_QNOVA_RUN_COMMAND",
    ]

    for marker in required:
        if marker not in result.stdout:
            print(result.stdout)
            raise SystemExit(f"MISSING RUN MARKER: {marker}")

    if not out.exists():
        raise SystemExit(f"MISSING OUT QBC: {out}")

    qbc_text = out.read_text(encoding="utf-8")
    if "FF" in qbc_text.split():
        raise SystemExit(f"UNKNOWN OPCODE FF FOUND: {out}")

    for suffix in [".json", ".pool.json", ".expanded.qnova"]:
        side = Path(str(out) + suffix)
        if not side.exists():
            raise SystemExit(f"MISSING SIDE FILE: {side}")
        if side.stat().st_size <= 0:
            raise SystemExit(f"EMPTY SIDE FILE: {side}")

run_source(QN_SRC, QN_OUT, "QBIT_NOVA_INSTALL_QN_V03")
run_source(QNOVA_SRC, QNOVA_OUT, "QBIT_NOVA_QBC_FILE_RUNNER_V03")

print("QBIT_NOVA_QN_SOURCE_SPEC_V03_GREEN")
