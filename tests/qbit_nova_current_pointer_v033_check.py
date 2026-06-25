#!/usr/bin/env python3
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "QBIT_NOVA_CURRENT_POINTER_V0_3_3.md"
QNOVA = ROOT / "tools" / "qnova"
INSTALL_QN = ROOT / "examples" / "v2" / "qbit_nova_install_v03.qn"

for p in [DOC, QNOVA, INSTALL_QN]:
    if not p.exists():
        raise SystemExit(f"MISSING: {p}")

text = DOC.read_text(encoding="utf-8")

checks = [
    "QBIT_NOVA_CURRENT_POINTER_V033",
    "QBIT NOVA language/core only",
    "qbit-nova-v1.4.0-dev-qn-source-spec-v03-green",
    "qbit-nova-v1.4.0-dev-qnova-generic-runner-v03-fix1-green",
    "qbit-nova-v1.4.0-dev-qn-manifest-runner-v03-green",
    "qbit-nova-v1.4.0-dev-qnova-manifest-command-v03-green",
    "./tools/qnova run examples/v2/qbit_nova_install_v03.qn",
    "./tools/qnova manifest examples/v2/qbit_nova_install_v03.qn",
    ".qn is short QBIT NOVA source",
    ".qnova is long QBIT NOVA source",
    ".qbc is QBIT NOVA compiled bytecode",
    "install.qn is a safe install manifest",
    "Python is bootstrap construction tool only",
    "QBIT NOVA .QN Manifest Command Polish v0.3.1",
    "No OS install execution",
    "No delete action",
    "No secret reading",
    "~/qbit-nova-labs/Universal-Dragon-Core-v02",
    "~/ud-github-sync",
]

for c in checks:
    if c not in text:
        raise SystemExit(f"MISSING DOC MARKER: {c}")

manifest = subprocess.run(
    [str(QNOVA), "manifest", str(INSTALL_QN)],
    cwd=str(ROOT),
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
)

if manifest.returncode != 0:
    print(manifest.stdout)
    raise SystemExit("QNOVA MANIFEST COMMAND FAILED")

for marker in [
    "QBIT_NOVA_QNOVA_MANIFEST_COMMAND_V03",
    "SAFE_QN_MANIFEST_READ",
    "QBIT_NOVA_INSTALL_QN_V03",
    "QBIT_NOVA_QNOVA_MANIFEST_COMMAND_V03_GREEN",
]:
    if marker not in manifest.stdout:
        print(manifest.stdout)
        raise SystemExit(f"MISSING MANIFEST MARKER: {marker}")

if '"os_execution": false' not in manifest.stdout:
    print(manifest.stdout)
    raise SystemExit("OS EXECUTION FLAG NOT FALSE")

if '"delete_action": false' not in manifest.stdout:
    print(manifest.stdout)
    raise SystemExit("DELETE ACTION FLAG NOT FALSE")

run_cmd = subprocess.run(
    [str(QNOVA), "run", str(INSTALL_QN)],
    cwd=str(ROOT),
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
)

if run_cmd.returncode != 0:
    print(run_cmd.stdout)
    raise SystemExit("QNOVA RUN COMMAND FAILED")

for marker in [
    "QBIT_NOVA_QNOVA_RUN_COMMAND_V03",
    "QBIT_NOVA_INSTALL_QN_V03",
    "QBIT_NOVA_QNOVA_RUN_COMMAND_V03_GREEN",
]:
    if marker not in run_cmd.stdout:
        print(run_cmd.stdout)
        raise SystemExit(f"MISSING RUN MARKER: {marker}")

print("QBIT_NOVA_CURRENT_POINTER_V033_GREEN")
