#!/usr/bin/env python3
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "QBIT_NOVA_CURRENT_POINTER_V0_5_0.md"
QNOVA = ROOT / "tools" / "qnova"
CORE_QN = ROOT / "examples" / "v2" / "core_actions_v05.qn"
INSTALL_QN = ROOT / "examples" / "v2" / "qbit_nova_install_v03.qn"

for p in [DOC, QNOVA, CORE_QN, INSTALL_QN]:
    if not p.exists():
        raise SystemExit(f"MISSING: {p}")

text = DOC.read_text(encoding="utf-8")

checks = [
    "QBIT_NOVA_CURRENT_POINTER_V050",
    "QBIT NOVA language/core only",
    "qbit-nova-v1.4.0-dev-core-action-library-v05-green",
    "check",
    "backup",
    "validate",
    "rollback",
    "learn",
    "emit",
    "safe_stage: true",
    "os_execution: false",
    "delete_action: false",
    "Unknown actions must not silently pass",
    "QBIT NOVA Guard / Approval Engine v0.6.0",
    "must not execute real OS install actions yet",
    "~/qbit-nova-labs/Universal-Dragon-Core-v02",
    "~/ud-github-sync",
]

for c in checks:
    if c not in text:
        raise SystemExit(f"MISSING DOC MARKER: {c}")

core = subprocess.run(
    [str(QNOVA), "run", str(CORE_QN)],
    cwd=str(ROOT),
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
)

if core.returncode != 0:
    print(core.stdout)
    raise SystemExit("CORE ACTION QN RUN FAILED")

for marker in [
    "QBIT_NOVA_QNOVA_RUN_COMMAND_V03",
    "QBIT_NOVA_CORE_ACTION_LIBRARY_V05",
    "QBIT_NOVA_QNOVA_RUN_COMMAND_V03_GREEN",
]:
    if marker not in core.stdout:
        print(core.stdout)
        raise SystemExit(f"MISSING CORE RUN MARKER: {marker}")

manifest = subprocess.run(
    [str(QNOVA), "manifest", str(INSTALL_QN)],
    cwd=str(ROOT),
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
)

if manifest.returncode != 0:
    print(manifest.stdout)
    raise SystemExit("MANIFEST COMMAND FAILED")

for marker in [
    "QBIT_NOVA_QNOVA_MANIFEST_COMMAND_V03_GREEN",
    "QBIT_NOVA_QNOVA_MANIFEST_SUMMARY_V04",
    "os_execution: false",
    "delete_action: false",
]:
    if marker not in manifest.stdout:
        print(manifest.stdout)
        raise SystemExit(f"MISSING MANIFEST MARKER: {marker}")

print("QBIT_NOVA_CURRENT_POINTER_V050_GREEN")
