#!/usr/bin/env python3
from pathlib import Path
import os
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "QBIT_NOVA_INSTALLER_V0_2.md"
SRC = ROOT / "examples" / "v2" / "qbit_nova_installer_v02.qnova"
INSTALLER = ROOT / "tools" / "install_qnova_v02.sh"
TMP_BIN = ROOT / ".tmp" / "qbit_nova_installer_v02_bin"

for p in [DOC, SRC, INSTALLER]:
    if not p.exists():
        raise SystemExit(f"MISSING: {p}")

doc = DOC.read_text(encoding="utf-8")
for marker in [
    "QBIT NOVA Installer v0.2",
    "QBIT_NOVA_INSTALLER_V02",
    "qnova examples/v2/qbit_nova_cli_launcher_v02.qnova",
]:
    if marker not in doc:
        raise SystemExit(f"MISSING DOC MARKER: {marker}")

source = SRC.read_text(encoding="utf-8")
for marker in [
    "@nova.v02",
    "q.intent.installer",
    "> QBIT_NOVA_INSTALLER_V02",
]:
    if marker not in source:
        raise SystemExit(f"MISSING SOURCE MARKER: {marker}")

TMP_BIN.mkdir(parents=True, exist_ok=True)

env = os.environ.copy()
env["QBIT_NOVA_INSTALL_BIN"] = str(TMP_BIN)

run = subprocess.run(
    [str(INSTALLER)],
    cwd=str(ROOT),
    env=env,
    text=True,
    capture_output=True,
)

if run.returncode != 0:
    raise SystemExit(run.stdout + run.stderr)

out = run.stdout + run.stderr

for marker in [
    "QBIT_NOVA_INSTALLER_V02",
    "QBIT_NOVA_INSTALLER_V02_GREEN",
]:
    if marker not in out:
        raise SystemExit(f"MISSING INSTALL OUTPUT MARKER: {marker}")

qnova = TMP_BIN / "qnova"
if not qnova.exists():
    raise SystemExit("MISSING INSTALLED qnova")

run2 = subprocess.run(
    [str(qnova), str(ROOT / "examples" / "v2" / "qbit_nova_cli_launcher_v02.qnova")],
    cwd=str(ROOT),
    text=True,
    capture_output=True,
)

if run2.returncode != 0:
    raise SystemExit(run2.stdout + run2.stderr)

if "QBIT_NOVA_SYNTAX_V02_GREEN" not in (run2.stdout + run2.stderr):
    raise SystemExit("INSTALLED qnova DID NOT RUN")

print("QBIT_NOVA_INSTALLER_V02_GREEN")
