#!/usr/bin/env python3
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "QBIT_NOVA_CURRENT_POINTER_V0_6_0.md"
QNOVA = ROOT / "tools" / "qnova"
GUARD_QN = ROOT / "examples" / "v2" / "guard_approval_v06.qn"
INSTALL_QN = ROOT / "examples" / "v2" / "qbit_nova_install_v03.qn"

for p in [DOC, QNOVA, GUARD_QN, INSTALL_QN]:
    if not p.exists():
        raise SystemExit(f"MISSING: {p}")

text = DOC.read_text(encoding="utf-8")

checks = [
    "QBIT_NOVA_CURRENT_POINTER_V060",
    "QBIT NOVA language/core only",
    "qbit-nova-v1.4.0-dev-guard-approval-engine-v06-green",
    "QBIT NOVA Guard / Approval Engine v0.6",
    "Allowed:",
    "Needs human approval:",
    "Blocked:",
    "check",
    "backup",
    "validate",
    "rollback",
    "learn",
    "emit",
    "install",
    "write_file",
    "network",
    "delete",
    "remove",
    "rmdir",
    "secret",
    "token",
    "unknown action",
    "safe_stage: true",
    "os_execution: false",
    "delete_action: false",
    "QBIT NOVA Safe File Writer / Project Generator v0.7.0",
    "must not delete files",
    "must not read secrets",
    "must not execute OS install actions yet",
    "~/qbit-nova-labs/Universal-Dragon-Core-v02",
    "~/ud-github-sync",
]

for c in checks:
    if c not in text:
        raise SystemExit(f"MISSING DOC MARKER: {c}")

guard_run = subprocess.run(
    [str(QNOVA), "run", str(GUARD_QN)],
    cwd=str(ROOT),
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
)

if guard_run.returncode != 0:
    print(guard_run.stdout)
    raise SystemExit("GUARD QN RUN FAILED")

for marker in [
    "QBIT_NOVA_QNOVA_RUN_COMMAND_V03",
    "QBIT_NOVA_GUARD_APPROVAL_ENGINE_V06",
    "QBIT_NOVA_QNOVA_RUN_COMMAND_V03_GREEN",
]:
    if marker not in guard_run.stdout:
        print(guard_run.stdout)
        raise SystemExit(f"MISSING GUARD RUN MARKER: {marker}")

manifest = subprocess.run(
    [str(QNOVA), "manifest", str(INSTALL_QN)],
    cwd=str(ROOT),
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
)

if manifest.returncode != 0:
    print(manifest.stdout)
    raise SystemExit("INSTALL MANIFEST FAILED")

for marker in [
    "QBIT_NOVA_QNOVA_MANIFEST_COMMAND_V03_GREEN",
    "QBIT_NOVA_QNOVA_MANIFEST_SUMMARY_V04",
    "os_execution: false",
    "delete_action: false",
]:
    if marker not in manifest.stdout:
        print(manifest.stdout)
        raise SystemExit(f"MISSING MANIFEST MARKER: {marker}")

print("QBIT_NOVA_CURRENT_POINTER_V060_GREEN")
