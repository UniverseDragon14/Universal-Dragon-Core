#!/usr/bin/env python3
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "QBIT_NOVA_CLI_LAUNCHER_V0_2.md"
SRC = ROOT / "examples" / "v2" / "qbit_nova_cli_launcher_v02.qnova"
CLI = ROOT / "tools" / "qnova"

for p in [DOC, SRC, CLI]:
    if not p.exists():
        raise SystemExit(f"MISSING: {p}")

doc = DOC.read_text(encoding="utf-8")
for marker in [
    "QBIT NOVA CLI Launcher v0.2",
    "./tools/qnova",
    "QBIT_NOVA_CLI_LAUNCHER_V02",
]:
    if marker not in doc:
        raise SystemExit(f"MISSING DOC MARKER: {marker}")

source = SRC.read_text(encoding="utf-8")
for marker in [
    "@nova.v02",
    "q.intent.cli_launcher",
    "> QBIT_NOVA_CLI_LAUNCHER_V02",
]:
    if marker not in source:
        raise SystemExit(f"MISSING SOURCE MARKER: {marker}")

run = subprocess.run(
    [str(CLI), str(SRC)],
    cwd=str(ROOT),
    text=True,
    capture_output=True,
)

if run.returncode != 0:
    raise SystemExit(run.stdout + run.stderr)

out = run.stdout + run.stderr

for marker in [
    "QBIT_NOVA_SYNTAX_V02",
    "QBIT_NOVA_CLI_LAUNCHER_V02",
    "QBIT_NOVA_SYNTAX_V02_GREEN",
]:
    if marker not in out:
        raise SystemExit(f"MISSING CLI OUTPUT MARKER: {marker}")

run2 = subprocess.run(
    [str(CLI), "run", str(SRC)],
    cwd=str(ROOT),
    text=True,
    capture_output=True,
)

if run2.returncode != 0:
    raise SystemExit(run2.stdout + run2.stderr)

if "QBIT_NOVA_CLI_LAUNCHER_V02" not in (run2.stdout + run2.stderr):
    raise SystemExit("RUN MODE OUTPUT MISSING")

print("QBIT_NOVA_CLI_LAUNCHER_V02_GREEN")
