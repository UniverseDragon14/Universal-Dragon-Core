#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path, PurePosixPath

TOOLS_DIR = Path(__file__).resolve().parent
ROOT = TOOLS_DIR.parent

if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import qbit_nova_guard_approval_v06 as guard

MARKER = "QBIT_NOVA_SAFE_FILE_WRITER_V07"
VERSION = "0.7.0"

MODE_METADATA_ONLY = "SAFE_FILE_WRITE_METADATA_ONLY"
MODE_GENERATED_WRITE = "SAFE_GENERATED_FILE_WRITE"

DECISION_SUCCESS = "success"
DECISION_BLOCKED = guard.DECISION_BLOCKED
DECISION_NEEDS_APPROVAL = guard.DECISION_NEEDS_APPROVAL

SAFE_OUTPUT_ROOT = ROOT / ".tmp" / "qbit-generated-v07"
SAFE_OUTPUT_ROOT_LABEL = ".tmp/qbit-generated-v07"
SENSITIVE_NAME_MARKERS = (".env", "secret", "token", "key", "credential")
WRITE_ACTION = "write_file"


def safe_output_root() -> Path:
    return SAFE_OUTPUT_ROOT


def _root_relative(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _base_metadata(
    *,
    action: object,
    decision: str,
    mode: str,
    path: object = "",
    reason: str,
    approval_required: bool,
    written: bool,
    success: bool,
    guard_metadata: dict | None = None,
) -> dict:
    metadata = {
        "marker": MARKER,
        "version": VERSION,
        "mode": mode,
        "action": guard.normalize_action_name(action),
        "decision": decision,
        "safe_stage": True,
        "os_execution": False,
        "delete_action": False,
        "approval_required": approval_required,
        "written": written,
        "success": success,
        "path": str(path),
        "safe_output_root": SAFE_OUTPUT_ROOT_LABEL,
        "reason": reason,
    }

    if guard_metadata is not None:
        metadata["guard_marker"] = guard_metadata.get("marker")
        metadata["guard_decision"] = guard_metadata.get("decision")
        metadata["guard_reason"] = guard_metadata.get("reason")

    return metadata


def _normalize_requested_path(path: object) -> str:
    return str(path or "").strip().replace("\\", "/")


def _is_absolute_path(raw_path: str) -> bool:
    return raw_path.startswith("/") or re.match(r"^[A-Za-z]:/", raw_path) is not None


def _strip_safe_root_prefix(parts: tuple[str, ...]) -> tuple[str, ...]:
    if parts[:2] == (".tmp", "qbit-generated-v07"):
        return parts[2:]
    return parts


def safe_relative_path(path: object) -> tuple[bool, str, str]:
    raw_path = _normalize_requested_path(path)

    if not raw_path:
        return False, "", "Path is empty."

    if raw_path.startswith("~"):
        return False, raw_path, "Home-relative paths are blocked."

    if _is_absolute_path(raw_path):
        return False, raw_path, "Absolute paths are blocked."

    if raw_path.endswith("/"):
        return False, raw_path, "Directory paths are blocked; write a text file path."

    pure = PurePosixPath(raw_path)
    parts = tuple(part for part in pure.parts if part not in ("", "."))
    parts = _strip_safe_root_prefix(parts)

    if not parts:
        return False, raw_path, "Path must name a file under the safe output root."

    if any(part == ".." for part in parts):
        return False, raw_path, "Parent traversal is blocked."

    for part in parts:
        lowered = part.lower()
        if any(marker in lowered for marker in SENSITIVE_NAME_MARKERS):
            return False, raw_path, "Sensitive file or folder names are blocked."

    relative = PurePosixPath(*parts).as_posix()
    return True, relative, "Path is inside the safe generated output root."


def _safe_destination(relative_path: str) -> tuple[bool, Path, str]:
    root = SAFE_OUTPUT_ROOT.resolve()
    destination = (SAFE_OUTPUT_ROOT / relative_path).resolve()

    if destination == root or root not in destination.parents:
        return False, destination, "Resolved path escapes the safe generated output root."

    return True, destination, "Resolved path is inside the safe generated output root."


def safe_file_write_metadata(
    path: object,
    *,
    action: object = WRITE_ACTION,
    approval: bool = False,
) -> dict:
    action_name = guard.normalize_action_name(action)
    guard_metadata = guard.guard_decision(action_name)

    if guard_metadata.get("decision") == DECISION_BLOCKED:
        return _base_metadata(
            action=action_name,
            decision=DECISION_BLOCKED,
            mode=MODE_METADATA_ONLY,
            path=path,
            reason=guard_metadata.get("reason", "Guard blocked action."),
            approval_required=False,
            written=False,
            success=False,
            guard_metadata=guard_metadata,
        )

    if action_name != WRITE_ACTION:
        return _base_metadata(
            action=action_name,
            decision=DECISION_BLOCKED,
            mode=MODE_METADATA_ONLY,
            path=path,
            reason="Safe file writer only accepts write_file actions.",
            approval_required=False,
            written=False,
            success=False,
            guard_metadata=guard_metadata,
        )

    path_ok, relative_path, path_reason = safe_relative_path(path)
    if not path_ok:
        return _base_metadata(
            action=action_name,
            decision=DECISION_BLOCKED,
            mode=MODE_METADATA_ONLY,
            path=path,
            reason=path_reason,
            approval_required=True,
            written=False,
            success=False,
            guard_metadata=guard_metadata,
        )

    dest_ok, destination, dest_reason = _safe_destination(relative_path)
    if not dest_ok:
        return _base_metadata(
            action=action_name,
            decision=DECISION_BLOCKED,
            mode=MODE_METADATA_ONLY,
            path=_root_relative(destination),
            reason=dest_reason,
            approval_required=True,
            written=False,
            success=False,
            guard_metadata=guard_metadata,
        )

    if approval is not True:
        return _base_metadata(
            action=action_name,
            decision=DECISION_NEEDS_APPROVAL,
            mode=MODE_METADATA_ONLY,
            path=_root_relative(destination),
            reason=guard_metadata.get("reason", "File writing requires explicit approval."),
            approval_required=True,
            written=False,
            success=False,
            guard_metadata=guard_metadata,
        )

    return _base_metadata(
        action=action_name,
        decision=DECISION_SUCCESS,
        mode=MODE_GENERATED_WRITE,
        path=_root_relative(destination),
        reason=f"{path_reason} {dest_reason}",
        approval_required=True,
        written=False,
        success=False,
        guard_metadata=guard_metadata,
    )


def write_safe_text_file(
    path: object,
    text: object,
    *,
    approval: bool = False,
    action: object = WRITE_ACTION,
) -> dict:
    metadata = safe_file_write_metadata(path, action=action, approval=approval)
    if metadata.get("decision") != DECISION_SUCCESS:
        return metadata

    destination = ROOT / metadata["path"]
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = str(text)
    destination.write_text(payload, encoding="utf-8")

    metadata.update({
        "written": True,
        "success": True,
        "bytes_written": len(payload.encode("utf-8")),
        "reason": "Approved safe text file written under the generated output root.",
    })
    return metadata


def _sample_project_files() -> tuple[tuple[str, str], ...]:
    manifest = {
        "marker": MARKER,
        "name": "sample_qbit_project",
        "language": "QBIT NOVA",
        "safe_stage": True,
        "os_execution": False,
        "delete_action": False,
    }

    main_qn = "\n".join([
        "@nova.v07",
        "@brain.novakutty",
        "@creator.aslam",
        "@project.universal_dragon",
        "@team.askutty",
        "@law.qbit_nova_identity_only",
        "@law.bootstrap_tool_only",
        "@law.safe_generated_project_only",
        "@law.no_os_execution",
        "@law.no_delete_action",
        "",
        "q.intent.safe_generated_sample_project_v07",
        "q.package.sample_qbit_project",
        "q.target.safe_generated_output",
        "",
        "g.intent:",
        "? check.safe_output_root",
        "+ validate.generated_project_files",
        "+ learn.safe_generation_metadata",
        "+ emit.safe_writer_marker",
        "",
        f"> {MARKER}",
        "",
    ])

    return (
        (
            "sample_qbit_project/README.md",
            "# Sample QBIT Project\n\nGenerated by QBIT NOVA Safe File Writer v0.7.0.\n",
        ),
        (
            "sample_qbit_project/manifest.json",
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        ),
        (
            "sample_qbit_project/src/main.qn",
            main_qn,
        ),
    )


def generate_sample_project(*, approval: bool = True) -> dict:
    results = [
        write_safe_text_file(path, text, approval=approval)
        for path, text in _sample_project_files()
    ]
    written = all(item.get("written") is True for item in results)
    decision = DECISION_SUCCESS if written else DECISION_NEEDS_APPROVAL

    return {
        "marker": MARKER,
        "version": VERSION,
        "mode": MODE_GENERATED_WRITE if written else MODE_METADATA_ONLY,
        "decision": decision,
        "safe_stage": True,
        "os_execution": False,
        "delete_action": False,
        "approval_required": True,
        "written": written,
        "success": written,
        "path": f"{SAFE_OUTPUT_ROOT_LABEL}/sample_qbit_project/",
        "safe_output_root": SAFE_OUTPUT_ROOT_LABEL,
        "reason": "Sample QBIT project generated safely." if written else "Sample QBIT project requires approval.",
        "files": results,
    }


def plan_metadata() -> dict:
    return {
        "marker": MARKER,
        "version": VERSION,
        "mode": MODE_METADATA_ONLY,
        "decision": "plan",
        "safe_stage": True,
        "os_execution": False,
        "delete_action": False,
        "approval_required": False,
        "written": False,
        "success": True,
        "path": SAFE_OUTPUT_ROOT_LABEL,
        "safe_output_root": SAFE_OUTPUT_ROOT_LABEL,
        "reason": "Plan only; no files written.",
        "guard_engine": guard.MARKER,
        "write_action": WRITE_ACTION,
        "blocked_actions": guard.blocked_action_names(),
        "sensitive_name_markers": SENSITIVE_NAME_MARKERS,
    }


def _print_result(result: dict) -> None:
    print(MARKER)
    print(json.dumps(result, indent=2, ensure_ascii=False))


def main(argv: list[str]) -> int:
    command = argv[0] if argv else "plan"

    if command == "plan":
        _print_result(plan_metadata())
        return 0

    if command == "demo":
        result = generate_sample_project(approval=True)
        _print_result(result)
        if result.get("success") is True:
            print(f"{MARKER}_GREEN")
            return 0
        return 1

    print("Usage: qbit_nova_safe_file_writer_v07.py plan|demo")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
