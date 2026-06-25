#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
DOC = ROOT / "docs" / "QBIT_NOVA_SAFE_FILE_WRITER_V0_7.md"
SRC = ROOT / "examples" / "v2" / "safe_file_writer_v07.qn"
QNOVA = TOOLS / "qnova"
OUT = ROOT / ".tmp" / "safe-file-writer-v07" / "safe_file_writer_v07.qbc"
SAFE_ROOT = ROOT / ".tmp" / "qbit-generated-v07"

if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import qbit_nova_guard_approval_v06 as guard
import qbit_nova_safe_file_writer_v07 as writer

MARKER = "QBIT_NOVA_SAFE_FILE_WRITER_V07"

for p in [DOC, SRC, QNOVA, TOOLS / "qbit_nova_safe_file_writer_v07.py", TOOLS / "qbit_nova_guard_approval_v06.py"]:
    if not p.exists():
        raise SystemExit(f"MISSING: {p}")

doc = DOC.read_text(encoding="utf-8")
for marker in [
    MARKER,
    "tools/qbit_nova_guard_approval_v06.py",
    ".tmp/qbit-generated-v07/",
    ".tmp/qbit-generated-v07/sample_qbit_project/",
    "SAFE_FILE_WRITE_METADATA_ONLY",
    "SAFE_GENERATED_FILE_WRITE",
    "approval=True",
    "approval=False",
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
    "unknown action",
    "./tools/qnova run examples/v2/safe_file_writer_v07.qn",
    "Generated QBC must not contain standalone FF opcode",
]:
    if marker not in doc:
        raise SystemExit(f"MISSING DOC MARKER: {marker}")

if writer.MARKER != MARKER:
    raise SystemExit("BAD WRITER MARKER")

if writer.safe_output_root() != SAFE_ROOT:
    raise SystemExit(f"BAD SAFE ROOT: {writer.safe_output_root()}")

plan = writer.plan_metadata()
for key, expected in {
    "marker": MARKER,
    "version": "0.7.0",
    "mode": "SAFE_FILE_WRITE_METADATA_ONLY",
    "safe_stage": True,
    "os_execution": False,
    "delete_action": False,
    "approval_required": False,
    "written": False,
}.items():
    if plan.get(key) != expected:
        raise SystemExit(f"BAD PLAN {key}: {plan.get(key)}")

if plan.get("guard_engine") != guard.MARKER:
    raise SystemExit("PLAN MUST USE GUARD ENGINE")


def assert_common(metadata: dict, *, written: bool) -> None:
    for key, expected in {
        "marker": MARKER,
        "safe_stage": True,
        "os_execution": False,
        "delete_action": False,
        "written": written,
    }.items():
        if metadata.get(key) != expected:
            raise SystemExit(f"BAD METADATA {key}: {metadata.get(key)}")
    if not metadata.get("reason"):
        raise SystemExit("MISSING METADATA REASON")
    if metadata.get("guard_marker") not in (None, guard.MARKER):
        raise SystemExit(f"BAD GUARD MARKER: {metadata.get('guard_marker')}")


needs_approval = writer.write_safe_text_file("approval_check.txt", "not written\n", approval=False)
assert_common(needs_approval, written=False)
if needs_approval.get("decision") != "needs_approval":
    raise SystemExit(f"BAD APPROVAL DECISION: {needs_approval}")
if needs_approval.get("mode") != "SAFE_FILE_WRITE_METADATA_ONLY":
    raise SystemExit("APPROVAL FALSE MUST BE METADATA ONLY")
if (SAFE_ROOT / "approval_check.txt").exists():
    raise SystemExit("FILE WRITTEN WITHOUT APPROVAL")

approved = writer.write_safe_text_file("tests/approved_write.txt", "QBIT NOVA SAFE WRITE\n", approval=True)
assert_common(approved, written=True)
if approved.get("decision") != "success":
    raise SystemExit(f"BAD APPROVED DECISION: {approved}")
if approved.get("mode") != "SAFE_GENERATED_FILE_WRITE":
    raise SystemExit("APPROVED WRITE MUST USE GENERATED WRITE MODE")

approved_path = ROOT / approved["path"]
if not approved_path.exists():
    raise SystemExit(f"MISSING APPROVED FILE: {approved_path}")
if approved_path.resolve().is_relative_to(SAFE_ROOT.resolve()) is not True:
    raise SystemExit(f"APPROVED FILE OUTSIDE SAFE ROOT: {approved_path}")
if approved_path.read_text(encoding="utf-8") != "QBIT NOVA SAFE WRITE\n":
    raise SystemExit("BAD APPROVED FILE CONTENT")

for bad_path in [
    "/tmp/qbit_escape.txt",
    "../qbit_escape.txt",
    "nested/../qbit_escape.txt",
    ".tmp/qbit-generated-v07/../qbit_escape.txt",
    ".env",
    "safe/secret_notes.txt",
    "safe/token_notes.txt",
    "safe/api_key.txt",
    "safe/credential_notes.txt",
]:
    blocked = writer.write_safe_text_file(bad_path, "blocked\n", approval=True)
    assert_common(blocked, written=False)
    if blocked.get("decision") != "blocked":
        raise SystemExit(f"UNSAFE PATH NOT BLOCKED: {bad_path}: {blocked}")
    if blocked.get("mode") != "SAFE_FILE_WRITE_METADATA_ONLY":
        raise SystemExit(f"UNSAFE PATH NOT METADATA ONLY: {bad_path}")

for action in ["delete", "remove", "rmdir", "format_disk"]:
    blocked = writer.write_safe_text_file("tests/action_blocked.txt", "blocked\n", approval=True, action=action)
    assert_common(blocked, written=False)
    if blocked.get("decision") != "blocked":
        raise SystemExit(f"UNSAFE ACTION NOT BLOCKED: {action}: {blocked}")
    if blocked.get("guard_marker") != guard.MARKER:
        raise SystemExit(f"UNSAFE ACTION MUST GO THROUGH GUARD: {action}")

install = writer.write_safe_text_file("tests/install_blocked.txt", "blocked\n", approval=True, action="install")
assert_common(install, written=False)
if install.get("decision") != "blocked":
    raise SystemExit(f"INSTALL ACTION MUST BE BLOCKED BY WRITER: {install}")
if install.get("guard_decision") != "needs_approval":
    raise SystemExit("INSTALL ACTION MUST STILL RECORD GUARD DECISION")

project = writer.generate_sample_project(approval=True)
for key, expected in {
    "marker": MARKER,
    "mode": "SAFE_GENERATED_FILE_WRITE",
    "safe_stage": True,
    "os_execution": False,
    "delete_action": False,
    "approval_required": True,
    "written": True,
    "success": True,
}.items():
    if project.get(key) != expected:
        raise SystemExit(f"BAD PROJECT {key}: {project.get(key)}")

expected_project_files = [
    SAFE_ROOT / "sample_qbit_project" / "README.md",
    SAFE_ROOT / "sample_qbit_project" / "manifest.json",
    SAFE_ROOT / "sample_qbit_project" / "src" / "main.qn",
]
for p in expected_project_files:
    if not p.exists():
        raise SystemExit(f"MISSING GENERATED PROJECT FILE: {p}")
    if p.resolve().is_relative_to(SAFE_ROOT.resolve()) is not True:
        raise SystemExit(f"GENERATED PROJECT ESCAPED SAFE ROOT: {p}")

for item in project.get("files", []):
    generated_path = ROOT / item.get("path", "")
    if generated_path.resolve().is_relative_to(SAFE_ROOT.resolve()) is not True:
        raise SystemExit(f"BAD GENERATED METADATA PATH: {generated_path}")

result = subprocess.run(
    [str(QNOVA), "run", str(SRC), str(OUT)],
    cwd=str(ROOT),
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
)

if result.returncode != 0:
    print(result.stdout)
    raise SystemExit("SAFE FILE WRITER SOURCE RUN FAILED")

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

print("QBIT_NOVA_SAFE_FILE_WRITER_V07_GREEN")
