#!/usr/bin/env python3
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "QBIT_NOVA_CURRENT_POINTER_V0_4_0.md"
QNOVA = ROOT / "tools" / "qnova"
INSTALL_QN = ROOT / "examples" / "v2" / "qbit_nova_install_v03.qn"

for p in [DOC, QNOVA, INSTALL_QN]:
    if not p.exists():
        raise SystemExit(f"MISSING: {p}")

text = DOC.read_text(encoding="utf-8")

checks = [
    "QBIT_NOVA_CURRENT_POINTER_V040",
    "QBIT NOVA language/core only",
    "qbit-nova-v1.4.0-dev-qnova-command-polish-v04-green",
    "./tools/qnova help",
    "./tools/qnova version",
    "./tools/qnova run examples/v2/qbit_nova_install_v03.qn",
    "./tools/qnova manifest examples/v2/qbit_nova_install_v03.qn",
    ".qn is short QBIT NOVA source",
    ".qnova is long QBIT NOVA source",
    ".qbc is QBIT NOVA compiled bytecode",
    "Python is bootstrap construction tool only",
    "QBIT NOVA Core Action Library v0.5.0",
    "check",
    "backup",
    "validate",
    "rollback",
    "learn",
    "emit",
    "must not execute OS install actions yet",
    "~/qbit-nova-labs/Universal-Dragon-Core-v02",
    "~/ud-github-sync",
]

for c in checks:
    if c not in text:
        raise SystemExit(f"MISSING DOC MARKER: {c}")

help_cmd = subprocess.run(
    [str(QNOVA), "help"],
    cwd=str(ROOT),
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
)

if help_cmd.returncode != 0:
    print(help_cmd.stdout)
    raise SystemExit("QNOVA HELP FAILED")

for marker in [
    "QBIT NOVA command help",
    "available commands: run, manifest, help, version",
    "source extensions: .qn, .qnova, .ud",
    "safety note: no OS install, no delete, bootstrap only",
]:
    if marker not in help_cmd.stdout:
        print(help_cmd.stdout)
        raise SystemExit(f"MISSING HELP MARKER: {marker}")

version_cmd = subprocess.run(
    [str(QNOVA), "version"],
    cwd=str(ROOT),
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
)

if version_cmd.returncode != 0:
    print(version_cmd.stdout)
    raise SystemExit("QNOVA VERSION FAILED")

for marker in [
    "QBIT_NOVA_QNOVA_COMMAND_POLISH_V04",
    "Current stage: v0.4.0",
    "Mode: SAFE_BOOTSTRAP_COMMAND",
]:
    if marker not in version_cmd.stdout:
        print(version_cmd.stdout)
        raise SystemExit(f"MISSING VERSION MARKER: {marker}")

manifest_cmd = subprocess.run(
    [str(QNOVA), "manifest", str(INSTALL_QN)],
    cwd=str(ROOT),
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
)

if manifest_cmd.returncode != 0:
    print(manifest_cmd.stdout)
    raise SystemExit("QNOVA MANIFEST FAILED")

for marker in [
    "QBIT_NOVA_QNOVA_MANIFEST_COMMAND_V03_GREEN",
    "QBIT_NOVA_QNOVA_MANIFEST_SUMMARY_V04",
    "intent: install_qbit_nova",
    "os_execution: false",
    "delete_action: false",
]:
    if marker not in manifest_cmd.stdout:
        print(manifest_cmd.stdout)
        raise SystemExit(f"MISSING MANIFEST MARKER: {marker}")

print("QBIT_NOVA_CURRENT_POINTER_V040_GREEN")
