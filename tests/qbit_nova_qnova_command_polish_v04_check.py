#!/usr/bin/env python3
from pathlib import Path
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "QBIT_NOVA_QNOVA_COMMAND_POLISH_V0_4.md"
QNOVA = ROOT / "tools" / "qnova"
INSTALL_QN = ROOT / "examples" / "v2" / "qbit_nova_install_v03.qn"
DEFAULT_OUT = ROOT / ".tmp" / "qnova-manifest-v03" / "qbit_nova_install_v03.qbc"

for p in [DOC, QNOVA, INSTALL_QN]:
    if not p.exists():
        raise SystemExit(f"MISSING: {p}")

doc = DOC.read_text(encoding="utf-8")
for marker in [
    "QBIT_NOVA_QNOVA_COMMAND_POLISH_V04",
    "./tools/qnova help",
    "./tools/qnova version",
    "available commands: run, manifest, help, version",
    "source extensions: .qn, .qnova, .ud",
    "output extension: .qbc",
    "safety note: no OS install, no delete, bootstrap only",
    "QBIT_NOVA_QNOVA_MANIFEST_SUMMARY_V04",
    "os_execution: false",
    "delete_action: false",
    "No OS install execution",
    "No delete action",
    "No secret reading",
    "FF opcode",
]:
    if marker not in doc:
        raise SystemExit(f"MISSING DOC MARKER: {marker}")


def run_qnova(*args: str) -> str:
    result = subprocess.run(
        [str(QNOVA), *args],
        cwd=str(ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    if result.returncode != 0:
        print(result.stdout)
        raise SystemExit(f"QNOVA COMMAND FAILED: {' '.join(args)}")

    return result.stdout


def parse_command_json(stdout: str) -> dict:
    start = stdout.find("{")
    end = stdout.rfind("}")
    if start == -1 or end == -1 or end < start:
        print(stdout)
        raise SystemExit("MISSING COMMAND JSON")
    return json.loads(stdout[start : end + 1])


help_lines = run_qnova("help").strip().splitlines()
expected_help = [
    "QBIT NOVA command help",
    "available commands: run, manifest, help, version",
    "source extensions: .qn, .qnova, .ud",
    "output extension: .qbc",
    "safety note: no OS install, no delete, bootstrap only",
]
if help_lines != expected_help:
    print("\n".join(help_lines))
    raise SystemExit("BAD HELP OUTPUT")

version_lines = run_qnova("version").strip().splitlines()
expected_version = [
    "QBIT_NOVA_QNOVA_COMMAND_POLISH_V04",
    "Current stage: v0.4.0",
    "Source: .qn / .qnova",
    "Bytecode: .qbc",
    "Mode: SAFE_BOOTSTRAP_COMMAND",
]
if version_lines != expected_version:
    print("\n".join(version_lines))
    raise SystemExit("BAD VERSION OUTPUT")

manifest_stdout = run_qnova("manifest", str(INSTALL_QN))
for marker in [
    "QBIT_NOVA_QNOVA_MANIFEST_COMMAND_V03",
    "QBIT_NOVA_QNOVA_MANIFEST_COMMAND_V03_GREEN",
    "QBIT_NOVA_QNOVA_MANIFEST_SUMMARY_V04",
    "intent: install_qbit_nova",
    "target: local_user_bin",
    "package: qnova",
    "output_marker: QBIT_NOVA_INSTALL_QN_V03",
    "os_execution: false",
    "delete_action: false",
]:
    if marker not in manifest_stdout:
        print(manifest_stdout)
        raise SystemExit(f"MISSING MANIFEST OUTPUT MARKER: {marker}")

payload = parse_command_json(manifest_stdout)
if payload.get("marker") != "QBIT_NOVA_QNOVA_MANIFEST_COMMAND_V03":
    raise SystemExit(f"BAD MANIFEST COMMAND MARKER: {payload.get('marker')}")

if Path(payload["qbc"]) != DEFAULT_OUT:
    raise SystemExit(f"BAD DEFAULT MANIFEST OUTPUT: {payload['qbc']}")

manifest = payload.get("manifest", {})
expected_manifest = {
    "intent": "install_qbit_nova",
    "target": "local_user_bin",
    "package": "qnova",
    "output_marker": "QBIT_NOVA_INSTALL_QN_V03",
    "os_execution": False,
    "delete_action": False,
}
for key, expected in expected_manifest.items():
    if manifest.get(key) != expected:
        raise SystemExit(f"BAD MANIFEST {key}: {manifest.get(key)}")

qbc = Path(payload["qbc"])
if not qbc.exists():
    raise SystemExit(f"MISSING QBC: {qbc}")

qbc_text = qbc.read_text(encoding="utf-8")
if "FF" in qbc_text.split():
    raise SystemExit("UNKNOWN OPCODE FF FOUND")

print("QBIT_NOVA_QNOVA_COMMAND_POLISH_V04_GREEN")
