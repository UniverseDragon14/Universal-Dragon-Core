#!/usr/bin/env python3
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "QBIT_NOVA_CURRENT_POINTER_V0_3_2.md"
QNOVA = ROOT / "tools" / "qnova"
INSTALL_QN = ROOT / "examples" / "v2" / "qbit_nova_install_v03.qn"
OUT = ROOT / ".tmp" / "qnova-run-v03" / "current_pointer_v032_install_check.qbc"

for p in [DOC, QNOVA, INSTALL_QN]:
    if not p.exists():
        raise SystemExit(f"MISSING: {p}")

text = DOC.read_text(encoding="utf-8")

checks = [
    "QBIT_NOVA_CURRENT_POINTER_V032",
    "QBIT NOVA language/core only",
    "qbit-nova-v1.4.0-dev-qn-source-spec-v03-green",
    "qbit-nova-v1.4.0-dev-qnova-generic-runner-v03-fix1-green",
    "qbit-nova-v1.4.0-dev-qbc-file-runner-v03-green",
    ".qn is short QBIT NOVA source",
    ".qnova is long QBIT NOVA source",
    ".qbc is QBIT NOVA compiled bytecode",
    "Python is bootstrap construction tool only",
    "QBIT NOVA .QN Manifest Runner v0.3",
    "manifest runner must not directly execute OS install actions",
    "~/qbit-nova-labs/Universal-Dragon-Core-v02",
    "~/ud-github-sync",
]

for c in checks:
    if c not in text:
        raise SystemExit(f"MISSING DOC MARKER: {c}")

result = subprocess.run(
    [str(QNOVA), "run", str(INSTALL_QN), str(OUT)],
    cwd=str(ROOT),
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
)

if result.returncode != 0:
    print(result.stdout)
    raise SystemExit("CURRENT POINTER V0.3.2 INSTALL QN RUN FAILED")

for marker in [
    "QBIT_NOVA_QNOVA_RUN_COMMAND_V03_GREEN",
    "QBIT_NOVA_INSTALL_QN_V03",
    "SAFE_QNOVA_RUN_COMMAND",
]:
    if marker not in result.stdout:
        print(result.stdout)
        raise SystemExit(f"MISSING RUN MARKER: {marker}")

if not OUT.exists():
    raise SystemExit(f"MISSING QBC OUT: {OUT}")

qbc_text = OUT.read_text(encoding="utf-8")
if "FF" in qbc_text.split():
    raise SystemExit("UNKNOWN OPCODE FF FOUND")

print("QBIT_NOVA_CURRENT_POINTER_V032_GREEN")
