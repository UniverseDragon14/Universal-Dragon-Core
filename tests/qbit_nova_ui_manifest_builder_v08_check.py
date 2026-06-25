#!/usr/bin/env python3
from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
DOC = ROOT / "docs" / "QBIT_NOVA_UI_MANIFEST_BUILDER_V0_8.md"
SRC = ROOT / "examples" / "v2" / "ui_manifest_v08.qn"
QNOVA = TOOLS / "qnova"
OUT = ROOT / ".tmp" / "ui-manifest-builder-v08" / "ui_manifest_v08.qbc"
SAFE_ROOT = ROOT / ".tmp" / "qbit-generated-v08"
MANIFEST_PATH = SAFE_ROOT / "novakutty_ui_manifest" / "manifest.json"
README_PATH = SAFE_ROOT / "novakutty_ui_manifest" / "README.md"

if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import qbit_nova_guard_approval_v06 as guard
import qbit_nova_safe_file_writer_v07 as safe_writer
import qbit_nova_ui_manifest_builder_v08 as builder

MARKER = "QBIT_NOVA_UI_MANIFEST_BUILDER_V08"
SENSITIVE_MARKERS = (".env", "secret", "token", "key", "credential")

for p in [DOC, SRC, QNOVA, TOOLS / "qbit_nova_ui_manifest_builder_v08.py"]:
    if not p.exists():
        raise SystemExit(f"MISSING: {p}")

doc = DOC.read_text(encoding="utf-8")
for marker in [
    MARKER,
    "tools/qbit_nova_safe_file_writer_v07.py",
    "tools/qbit_nova_guard_approval_v06.py",
    ".tmp/qbit-generated-v08/",
    ".tmp/qbit-generated-v08/novakutty_ui_manifest/manifest.json",
    "SAFE_UI_MANIFEST_BUILDER",
    "hero",
    "text",
    "input",
    "button",
    "panel",
    "badge",
    "ask",
    "navigate",
    "emit",
    ".env",
    "secret",
    "token",
    "key",
    "credential",
    "./tools/qnova run examples/v2/ui_manifest_v08.qn",
    "Generated QBC must not contain standalone FF opcode",
    "No existing NovaKutty UI files are modified.",
]:
    if marker not in doc:
        raise SystemExit(f"MISSING DOC MARKER: {marker}")

if builder.MARKER != MARKER:
    raise SystemExit("BAD BUILDER MARKER")

if builder.safe_output_root() != SAFE_ROOT:
    raise SystemExit(f"BAD SAFE ROOT: {builder.safe_output_root()}")

if builder.ALLOWED_COMPONENT_TYPES != ("hero", "text", "input", "button", "panel", "badge"):
    raise SystemExit(f"BAD COMPONENT TYPES: {builder.ALLOWED_COMPONENT_TYPES}")

if builder.ALLOWED_ACTION_TYPES != ("ask", "navigate", "emit"):
    raise SystemExit(f"BAD ACTION TYPES: {builder.ALLOWED_ACTION_TYPES}")

if safe_writer.safe_output_root() != ROOT / ".tmp" / "qbit-generated-v07":
    raise SystemExit("BUILDER MUST NOT CHANGE V0.7 WRITER ROOT AT IMPORT")

plan = builder.plan_metadata()
for key, expected in {
    "marker": MARKER,
    "version": "0.8.0",
    "mode": "SAFE_UI_MANIFEST_BUILDER",
    "decision": "plan",
    "safe_stage": True,
    "os_execution": False,
    "delete_action": False,
    "generated_root": ".tmp/qbit-generated-v08/",
    "manifest_path": ".tmp/qbit-generated-v08/novakutty_ui_manifest/manifest.json",
    "components_count": 6,
    "actions_count": 3,
    "success": True,
    "output": MARKER,
}.items():
    if plan.get(key) != expected:
        raise SystemExit(f"BAD PLAN {key}: {plan.get(key)}")

if plan.get("guard_engine") != guard.MARKER:
    raise SystemExit("PLAN MUST USE GUARD ENGINE")

if plan.get("writer_marker") != safe_writer.MARKER:
    raise SystemExit("PLAN MUST USE SAFE WRITER")

if plan.get("guard_write_decision") != "needs_approval":
    raise SystemExit(f"BAD GUARD WRITE DECISION: {plan.get('guard_write_decision')}")

manifest = builder.build_ui_manifest()
for field in [
    "app_name",
    "title",
    "subtitle",
    "route",
    "theme",
    "components",
    "actions",
    "safety",
]:
    if field not in manifest:
        raise SystemExit(f"MISSING MANIFEST FIELD: {field}")

validation = builder.validate_ui_manifest(manifest)
if validation.get("decision") != "allowed":
    raise SystemExit(f"DEFAULT MANIFEST NOT ALLOWED: {validation}")

component_types = tuple(item.get("type") for item in manifest.get("components", []))
if component_types != builder.ALLOWED_COMPONENT_TYPES:
    raise SystemExit(f"DEFAULT MANIFEST MUST EXERCISE ALL COMPONENT TYPES: {component_types}")

action_types = tuple(item.get("type") for item in manifest.get("actions", []))
if action_types != builder.ALLOWED_ACTION_TYPES:
    raise SystemExit(f"DEFAULT MANIFEST MUST EXERCISE ALL ACTION TYPES: {action_types}")

bad_component = builder.build_ui_manifest()
bad_component["components"][0]["type"] = "chart"
blocked = builder.validate_ui_manifest(bad_component)
if blocked.get("decision") != "blocked":
    raise SystemExit(f"UNKNOWN COMPONENT TYPE NOT BLOCKED: {blocked}")

bad_action = builder.build_ui_manifest()
bad_action["actions"][0]["type"] = "submit"
blocked = builder.validate_ui_manifest(bad_action)
if blocked.get("decision") != "blocked":
    raise SystemExit(f"UNKNOWN ACTION TYPE NOT BLOCKED: {blocked}")

for marker in SENSITIVE_MARKERS:
    bad_name = builder.build_ui_manifest()
    bad_name["components"][0]["id"] = f"blocked_{marker}_name"
    blocked = builder.validate_ui_manifest(bad_name)
    if blocked.get("decision") != "blocked":
        raise SystemExit(f"SENSITIVE NAME NOT BLOCKED: {marker}: {blocked}")

bad_field = builder.build_ui_manifest()
bad_field["safety"]["api_key"] = "blocked"
blocked = builder.validate_ui_manifest(bad_field)
if blocked.get("decision") != "blocked":
    raise SystemExit(f"SENSITIVE FIELD NOT BLOCKED: {blocked}")

for bad_path in [
    "/tmp/out.json",
    "../out.json",
    ".tmp/qbit-generated-v07/manifest.json",
    ".tmp/qbit-generated-v08/../manifest.json",
    "novakutty_ui_manifest/api_key.json",
]:
    ok, _relative, _reason = builder.safe_relative_path(bad_path)
    if ok:
        raise SystemExit(f"UNSAFE PATH NOT BLOCKED: {bad_path}")

ok, relative, _reason = builder.safe_relative_path(".tmp/qbit-generated-v08/novakutty_ui_manifest/manifest.json")
if not ok or relative != "novakutty_ui_manifest/manifest.json":
    raise SystemExit(f"SAFE ROOT PREFIX NOT NORMALIZED: ok={ok} relative={relative}")

demo = builder.generate_ui_manifest_files(approval=True, include_readme=True)
for key, expected in {
    "marker": MARKER,
    "mode": "SAFE_UI_MANIFEST_BUILDER",
    "decision": "success",
    "safe_stage": True,
    "os_execution": False,
    "delete_action": False,
    "generated_root": ".tmp/qbit-generated-v08/",
    "manifest_path": ".tmp/qbit-generated-v08/novakutty_ui_manifest/manifest.json",
    "components_count": 6,
    "actions_count": 3,
    "written": True,
    "success": True,
    "output": MARKER,
}.items():
    if demo.get(key) != expected:
        raise SystemExit(f"BAD DEMO {key}: {demo.get(key)}")

for generated in [MANIFEST_PATH, README_PATH]:
    if not generated.exists():
        raise SystemExit(f"MISSING GENERATED FILE: {generated}")
    if generated.resolve().is_relative_to(SAFE_ROOT.resolve()) is not True:
        raise SystemExit(f"GENERATED FILE OUTSIDE SAFE ROOT: {generated}")
    lowered_path = generated.relative_to(SAFE_ROOT).as_posix().lower()
    if any(marker in lowered_path for marker in SENSITIVE_MARKERS):
        raise SystemExit(f"SENSITIVE GENERATED PATH: {generated}")

manifest_json = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
if manifest_json.get("marker") != MARKER:
    raise SystemExit(f"BAD GENERATED MANIFEST MARKER: {manifest_json.get('marker')}")

for field in [
    "app_name",
    "title",
    "subtitle",
    "route",
    "theme",
    "components",
    "actions",
    "safety",
]:
    if field not in manifest_json:
        raise SystemExit(f"MISSING GENERATED MANIFEST FIELD: {field}")

serialized_manifest = json.dumps(manifest_json, sort_keys=True).lower()
for marker in SENSITIVE_MARKERS:
    if marker in serialized_manifest:
        raise SystemExit(f"SENSITIVE TERM WRITTEN TO GENERATED MANIFEST: {marker}")

for item in demo.get("files", []):
    if item.get("marker") != safe_writer.MARKER:
        raise SystemExit(f"DEMO FILE MUST USE V0.7 WRITER: {item}")
    if item.get("guard_marker") != guard.MARKER:
        raise SystemExit(f"DEMO FILE MUST USE V0.6 GUARD: {item}")
    if item.get("written") is not True:
        raise SystemExit(f"DEMO FILE NOT WRITTEN: {item}")
    generated_path = ROOT / item.get("path", "")
    if generated_path.resolve().is_relative_to(SAFE_ROOT.resolve()) is not True:
        raise SystemExit(f"DEMO FILE OUTSIDE V0.8 ROOT: {generated_path}")

if safe_writer.safe_output_root() != ROOT / ".tmp" / "qbit-generated-v07":
    raise SystemExit("BUILDER MUST RESTORE V0.7 WRITER ROOT AFTER DEMO")

source_text = (TOOLS / "qbit_nova_ui_manifest_builder_v08.py").read_text(encoding="utf-8")
for forbidden in ["subprocess", "os.system", "shutil.rmtree", ".unlink(", ".rmdir("]:
    if forbidden in source_text:
        raise SystemExit(f"FORBIDDEN BUILDER SOURCE PATTERN: {forbidden}")

result = subprocess.run(
    [str(QNOVA), "run", str(SRC), str(OUT)],
    cwd=str(ROOT),
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
)

if result.returncode != 0:
    print(result.stdout)
    raise SystemExit("UI MANIFEST QN SOURCE RUN FAILED")

for marker in [
    "QBIT_NOVA_QNOVA_RUN_COMMAND_V03_GREEN",
    MARKER,
    "SAFE_QNOVA_RUN_COMMAND",
]:
    if marker not in result.stdout:
        print(result.stdout)
        raise SystemExit(f"MISSING RUN MARKER: {marker}")

if not OUT.exists():
    raise SystemExit(f"MISSING QBC: {OUT}")

qbc_text = OUT.read_text(encoding="utf-8")
if "FF" in qbc_text.split():
    raise SystemExit("UNKNOWN OPCODE FF FOUND")

for suffix in [".json", ".pool.json", ".expanded.qnova"]:
    side = Path(str(OUT) + suffix)
    if not side.exists():
        raise SystemExit(f"MISSING SIDE FILE: {side}")
    if side.stat().st_size <= 0:
        raise SystemExit(f"EMPTY SIDE FILE: {side}")

for command in ["plan", "demo"]:
    cli = subprocess.run(
        ["python3", str(TOOLS / "qbit_nova_ui_manifest_builder_v08.py"), command],
        cwd=str(ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if cli.returncode != 0:
        print(cli.stdout)
        raise SystemExit(f"BUILDER CLI FAILED: {command}")
    if MARKER not in cli.stdout:
        print(cli.stdout)
        raise SystemExit(f"BUILDER CLI MISSING MARKER: {command}")

print("QBIT_NOVA_UI_MANIFEST_BUILDER_V08_GREEN")
