#!/usr/bin/env python3
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "QBIT_NOVA_CURRENT_POINTER_V0_8_0.md"
QNOVA = ROOT / "tools" / "qnova"
UI_QN = ROOT / "examples" / "v2" / "ui_manifest_v08.qn"
INSTALL_QN = ROOT / "examples" / "v2" / "qbit_nova_install_v03.qn"
UI_TOOL = ROOT / "tools" / "qbit_nova_ui_manifest_builder_v08.py"
GEN_ROOT = ROOT / ".tmp" / "qbit-generated-v08"

for p in [DOC, QNOVA, UI_QN, INSTALL_QN, UI_TOOL]:
    if not p.exists():
        raise SystemExit(f"MISSING: {p}")

text = DOC.read_text(encoding="utf-8")

checks = [
    "QBIT_NOVA_CURRENT_POINTER_V080",
    "QBIT NOVA language/core only",
    "qbit-nova-v1.4.0-dev-ui-manifest-builder-v08-green",
    ".tmp/qbit-generated-v08/",
    "Generated files must not be committed",
    "safe_stage: true",
    "os_execution: false",
    "delete_action: false",
    "unknown component types",
    "unknown action types",
    ".env",
    "secret",
    "token",
    "key",
    "credential",
    "delete",
    "remove",
    "rmdir",
    "hero",
    "text",
    "input",
    "button",
    "panel",
    "badge",
    "ask",
    "navigate",
    "emit",
    "./tools/qnova run examples/v2/ui_manifest_v08.qn",
    "python3 tools/qbit_nova_ui_manifest_builder_v08.py demo",
    "Universal Dragon Eve and WhatsApp bot are outside this chat scope",
    "QBIT NOVA v0.9.0 = NovaKutty UI Manifest Project Generator",
    "must not edit the existing NovaKutty UI yet",
    "must not touch business/dashboard/EVE",
    "~/qbit-nova-labs/Universal-Dragon-Core-v02",
    "~/ud-github-sync",
]

for c in checks:
    if c not in text:
        raise SystemExit(f"MISSING DOC MARKER: {c}")

ui_run = subprocess.run(
    [str(QNOVA), "run", str(UI_QN)],
    cwd=str(ROOT),
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
)

if ui_run.returncode != 0:
    print(ui_run.stdout)
    raise SystemExit("UI MANIFEST QN RUN FAILED")

for marker in [
    "QBIT_NOVA_QNOVA_RUN_COMMAND_V03",
    "QBIT_NOVA_UI_MANIFEST_BUILDER_V08",
    "QBIT_NOVA_QNOVA_RUN_COMMAND_V03_GREEN",
]:
    if marker not in ui_run.stdout:
        print(ui_run.stdout)
        raise SystemExit(f"MISSING UI RUN MARKER: {marker}")

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
    ["python3", str(UI_TOOL), "plan"],
    cwd=str(ROOT),
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
)

if plan.returncode != 0:
    print(plan.stdout)
    raise SystemExit("UI MANIFEST PLAN FAILED")

if "QBIT_NOVA_UI_MANIFEST_BUILDER_V08" not in plan.stdout:
    print(plan.stdout)
    raise SystemExit("MISSING PLAN MARKER")

demo = subprocess.run(
    ["python3", str(UI_TOOL), "demo"],
    cwd=str(ROOT),
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
)

if demo.returncode != 0:
    print(demo.stdout)
    raise SystemExit("UI MANIFEST DEMO FAILED")

if "QBIT_NOVA_UI_MANIFEST_BUILDER_V08_GREEN" not in demo.stdout:
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

src_status = subprocess.run(
    ["git", "status", "--short", "src"],
    cwd=str(ROOT),
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
)

if src_status.stdout.strip():
    print(src_status.stdout)
    raise SystemExit("SRC MODIFIED")

print("QBIT_NOVA_CURRENT_POINTER_V080_GREEN")
