#!/usr/bin/env python3
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "QBIT_NOVA_CURRENT_POINTER_V0_7_0.md"
QNOVA = ROOT / "tools" / "qnova"
SAFE_QN = ROOT / "examples" / "v2" / "safe_file_writer_v07.qn"
INSTALL_QN = ROOT / "examples" / "v2" / "qbit_nova_install_v03.qn"
SAFE_TOOL = ROOT / "tools" / "qbit_nova_safe_file_writer_v07.py"
GEN_ROOT = ROOT / ".tmp" / "qbit-generated-v07"

for p in [DOC, QNOVA, SAFE_QN, INSTALL_QN, SAFE_TOOL]:
    if not p.exists():
        raise SystemExit(f"MISSING: {p}")

text = DOC.read_text(encoding="utf-8")

checks = [
    "QBIT_NOVA_CURRENT_POINTER_V070",
    "QBIT NOVA language/core only",
    "qbit-nova-v1.4.0-dev-safe-file-writer-v07-green",
    ".tmp/qbit-generated-v07/",
    "absolute paths",
    "parent traversal",
    ".env",
    "secret",
    "token",
    "key",
    "credential",
    "delete",
    "remove",
    "rmdir",
    "safe_stage: true",
    "os_execution: false",
    "delete_action: false",
    "Writing requires approval=True",
    "needs_approval",
    "./tools/qnova run examples/v2/safe_file_writer_v07.qn",
    "python3 tools/qbit_nova_safe_file_writer_v07.py demo",
    "QBIT NOVA UI Manifest Builder v0.8.0",
    "must not edit the existing NovaKutty UI yet",
    "must not touch business/dashboard/EVE",
    "~/qbit-nova-labs/Universal-Dragon-Core-v02",
    "~/ud-github-sync",
]

for c in checks:
    if c not in text:
        raise SystemExit(f"MISSING DOC MARKER: {c}")

safe_run = subprocess.run(
    [str(QNOVA), "run", str(SAFE_QN)],
    cwd=str(ROOT),
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
)

if safe_run.returncode != 0:
    print(safe_run.stdout)
    raise SystemExit("SAFE WRITER QN RUN FAILED")

for marker in [
    "QBIT_NOVA_QNOVA_RUN_COMMAND_V03",
    "QBIT_NOVA_SAFE_FILE_WRITER_V07",
    "QBIT_NOVA_QNOVA_RUN_COMMAND_V03_GREEN",
]:
    if marker not in safe_run.stdout:
        print(safe_run.stdout)
        raise SystemExit(f"MISSING SAFE RUN MARKER: {marker}")

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

plan = subprocess.run(
    ["python3", str(SAFE_TOOL), "plan"],
    cwd=str(ROOT),
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
)

if plan.returncode != 0:
    print(plan.stdout)
    raise SystemExit("SAFE WRITER PLAN FAILED")

if "QBIT_NOVA_SAFE_FILE_WRITER_V07" not in plan.stdout:
    print(plan.stdout)
    raise SystemExit("MISSING PLAN MARKER")

demo = subprocess.run(
    ["python3", str(SAFE_TOOL), "demo"],
    cwd=str(ROOT),
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
)

if demo.returncode != 0:
    print(demo.stdout)
    raise SystemExit("SAFE WRITER DEMO FAILED")

if "QBIT_NOVA_SAFE_FILE_WRITER_V07_GREEN" not in demo.stdout:
    print(demo.stdout)
    raise SystemExit("MISSING DEMO GREEN MARKER")

if not GEN_ROOT.exists():
    raise SystemExit(f"MISSING GENERATED ROOT: {GEN_ROOT}")

bad_parts = [".env", "secret", "token", "key", "credential"]
for p in GEN_ROOT.rglob("*"):
    if not p.is_file():
        continue
    rel = p.relative_to(GEN_ROOT)
    rel_text = str(rel).lower()
    if any(bad in rel_text for bad in bad_parts):
        raise SystemExit(f"BAD GENERATED FILE NAME: {rel}")

print("QBIT_NOVA_CURRENT_POINTER_V070_GREEN")
