#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from contextlib import contextmanager
from copy import deepcopy
from pathlib import Path, PurePosixPath

TOOLS_DIR = Path(__file__).resolve().parent
ROOT = TOOLS_DIR.parent

if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import qbit_nova_guard_approval_v06 as guard
import qbit_nova_safe_file_writer_v07 as safe_writer

MARKER = "QBIT_NOVA_UI_MANIFEST_BUILDER_V08"
VERSION = "0.8.0"
MODE = "SAFE_UI_MANIFEST_BUILDER"
BLOCKED_MODE = "SAFE_UI_MANIFEST_BLOCKED"

SAFE_OUTPUT_ROOT = ROOT / ".tmp" / "qbit-generated-v08"
SAFE_OUTPUT_ROOT_LABEL = ".tmp/qbit-generated-v08"
MANIFEST_DIR = "novakutty_ui_manifest"
MANIFEST_RELATIVE_PATH = f"{MANIFEST_DIR}/manifest.json"
README_RELATIVE_PATH = f"{MANIFEST_DIR}/README.md"
MANIFEST_PATH_LABEL = f"{SAFE_OUTPUT_ROOT_LABEL}/{MANIFEST_RELATIVE_PATH}"
README_PATH_LABEL = f"{SAFE_OUTPUT_ROOT_LABEL}/{README_RELATIVE_PATH}"

WRITE_ACTION = "write_file"
ALLOWED_COMPONENT_TYPES = ("hero", "text", "input", "button", "panel", "badge")
ALLOWED_ACTION_TYPES = ("ask", "navigate", "emit")
SENSITIVE_NAME_MARKERS = (".env", "secret", "token", "key", "credential")

REQUIRED_MANIFEST_FIELDS = (
    "app_name",
    "title",
    "subtitle",
    "route",
    "theme",
    "components",
    "actions",
    "safety",
)


def safe_output_root() -> Path:
    return SAFE_OUTPUT_ROOT


def _root_relative(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _contains_sensitive_marker(value: object) -> bool:
    lowered = str(value or "").lower()
    return any(marker in lowered for marker in SENSITIVE_NAME_MARKERS)


def _normalize_requested_path(path: object) -> str:
    return str(path or "").strip().replace("\\", "/")


def _is_absolute_path(raw_path: str) -> bool:
    return raw_path.startswith("/") or (len(raw_path) >= 3 and raw_path[1:3] == ":/")


def _strip_v08_safe_root_prefix(parts: tuple[str, ...]) -> tuple[str, ...]:
    if parts[:2] == (".tmp", "qbit-generated-v08"):
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
    parts = _strip_v08_safe_root_prefix(parts)

    if not parts:
        return False, raw_path, "Path must name a file under the safe v0.8 output root."

    if parts[0] == ".tmp":
        return False, raw_path, "Only .tmp/qbit-generated-v08/ is allowed as an explicit output root."

    if any(part == ".." for part in parts):
        return False, raw_path, "Parent traversal is blocked."

    for part in parts:
        if _contains_sensitive_marker(part):
            return False, raw_path, "Sensitive file or folder names are blocked."

    relative = PurePosixPath(*parts).as_posix()
    root = SAFE_OUTPUT_ROOT.resolve()
    destination = (SAFE_OUTPUT_ROOT / relative).resolve()

    if destination == root or root not in destination.parents:
        return False, raw_path, "Resolved path escapes the safe v0.8 output root."

    return True, relative, "Path is inside the safe v0.8 generated output root."


def _base_metadata(
    *,
    decision: str,
    reason: str,
    manifest: dict | None = None,
    written: bool = False,
    success: bool = False,
) -> dict:
    components_count = 0
    actions_count = 0
    app_name = ""

    if isinstance(manifest, dict):
        components = manifest.get("components", [])
        actions = manifest.get("actions", [])
        components_count = len(components) if isinstance(components, list) else 0
        actions_count = len(actions) if isinstance(actions, list) else 0
        app_name = str(manifest.get("app_name", ""))

    return {
        "marker": MARKER,
        "version": VERSION,
        "mode": MODE if decision != "blocked" else BLOCKED_MODE,
        "decision": decision,
        "safe_stage": True,
        "os_execution": False,
        "delete_action": False,
        "app_name": app_name,
        "generated_root": f"{SAFE_OUTPUT_ROOT_LABEL}/",
        "manifest_path": MANIFEST_PATH_LABEL,
        "components_count": components_count,
        "actions_count": actions_count,
        "written": written,
        "success": success,
        "guard_engine": guard.MARKER,
        "writer_marker": safe_writer.MARKER,
        "reason": reason,
        "output": MARKER,
    }


def _blocked_metadata(reason: str, manifest: dict | None = None) -> dict:
    return _base_metadata(
        decision="blocked",
        reason=reason,
        manifest=manifest,
        written=False,
        success=False,
    )


def _validate_safe_value(value: object, location: str) -> tuple[bool, str]:
    if isinstance(value, dict):
        for key, item in value.items():
            key_text = str(key)
            if _contains_sensitive_marker(key_text):
                return False, f"Sensitive field name blocked at {location}.{key_text}."
            ok, reason = _validate_safe_value(item, f"{location}.{key_text}")
            if not ok:
                return False, reason
        return True, "Safe value."

    if isinstance(value, list):
        for index, item in enumerate(value):
            ok, reason = _validate_safe_value(item, f"{location}[{index}]")
            if not ok:
                return False, reason
        return True, "Safe value."

    if isinstance(value, str) and _contains_sensitive_marker(value):
        return False, f"Sensitive name blocked at {location}."

    return True, "Safe value."


def default_ui_manifest() -> dict:
    manifest = {
        "marker": MARKER,
        "version": VERSION,
        "mode": MODE,
        "safe_stage": True,
        "os_execution": False,
        "delete_action": False,
        "app_name": "novakutty_manifest_demo",
        "title": "NovaKutty Manifest Preview",
        "subtitle": "QBIT NOVA safe UI metadata only.",
        "route": "/novakutty/manifest-preview",
        "theme": {
            "name": "nova_safe",
            "tone": "calm",
            "palette": ["ink", "mint", "gold"],
        },
        "components": [
            {
                "id": "hero_intro",
                "type": "hero",
                "title": "NovaKutty Manifest Preview",
                "body": "A safe manifest description for a future UI stage.",
            },
            {
                "id": "summary_text",
                "type": "text",
                "text": "This file describes UI intent only.",
            },
            {
                "id": "question_input",
                "type": "input",
                "label": "Question",
                "placeholder": "Ask a QBIT NOVA question",
            },
            {
                "id": "ask_button",
                "type": "button",
                "label": "Ask",
                "action": "ask_action",
            },
            {
                "id": "status_panel",
                "type": "panel",
                "title": "Manifest Status",
                "body": "Safe stage ready.",
            },
            {
                "id": "safe_badge",
                "type": "badge",
                "label": "Manifest Only",
            },
        ],
        "actions": [
            {
                "id": "ask_action",
                "type": "ask",
                "label": "Ask NovaKutty",
                "target": "question_input",
            },
            {
                "id": "preview_action",
                "type": "navigate",
                "label": "Open Preview",
                "target": "/novakutty/manifest-preview",
            },
            {
                "id": "emit_action",
                "type": "emit",
                "label": "Emit Marker",
                "target": MARKER,
            },
        ],
        "safety": {
            "manifest_only": True,
            "safe_stage": True,
            "os_execution": False,
            "delete_action": False,
            "existing_ui_edit": False,
            "component_allowlist": list(ALLOWED_COMPONENT_TYPES),
            "action_allowlist": list(ALLOWED_ACTION_TYPES),
            "blocked_sensitive_names": True,
            "guard_marker": guard.MARKER,
            "writer_marker": safe_writer.MARKER,
            "generated_root": f"{SAFE_OUTPUT_ROOT_LABEL}/",
        },
        "generated_root": f"{SAFE_OUTPUT_ROOT_LABEL}/",
        "manifest_path": MANIFEST_PATH_LABEL,
        "components_count": 6,
        "actions_count": 3,
        "output": MARKER,
    }
    return manifest


def validate_ui_manifest(manifest: dict) -> dict:
    if not isinstance(manifest, dict):
        return _blocked_metadata("Manifest must be a metadata object.")

    for field in REQUIRED_MANIFEST_FIELDS:
        if field not in manifest:
            return _blocked_metadata(f"Missing required manifest field: {field}.", manifest)

    ok, reason = _validate_safe_value(manifest, "manifest")
    if not ok:
        return _blocked_metadata(reason, manifest)

    components = manifest.get("components")
    if not isinstance(components, list):
        return _blocked_metadata("Manifest components must be a list.", manifest)

    for index, component in enumerate(components):
        if not isinstance(component, dict):
            return _blocked_metadata(f"Component {index} must be an object.", manifest)

        component_type = str(component.get("type", "")).strip().lower()
        if component_type not in ALLOWED_COMPONENT_TYPES:
            return _blocked_metadata(f"Unknown component type blocked: {component_type}.", manifest)

    actions = manifest.get("actions")
    if not isinstance(actions, list):
        return _blocked_metadata("Manifest actions must be a list.", manifest)

    for index, action in enumerate(actions):
        if not isinstance(action, dict):
            return _blocked_metadata(f"Action {index} must be an object.", manifest)

        action_type = str(action.get("type", "")).strip().lower()
        if action_type not in ALLOWED_ACTION_TYPES:
            return _blocked_metadata(f"Unknown action type blocked: {action_type}.", manifest)

    if manifest.get("safe_stage") is not True:
        return _blocked_metadata("Manifest safe_stage must be true.", manifest)

    if manifest.get("os_execution") is not False:
        return _blocked_metadata("Manifest os_execution must be false.", manifest)

    if manifest.get("delete_action") is not False:
        return _blocked_metadata("Manifest delete_action must be false.", manifest)

    return _base_metadata(
        decision="allowed",
        reason="Safe UI manifest metadata validated.",
        manifest=manifest,
        written=False,
        success=True,
    )


def build_ui_manifest(spec: dict | None = None) -> dict:
    manifest = default_ui_manifest() if spec is None else deepcopy(spec)
    components = manifest.get("components", [])
    actions = manifest.get("actions", [])
    manifest["components_count"] = len(components) if isinstance(components, list) else 0
    manifest["actions_count"] = len(actions) if isinstance(actions, list) else 0
    manifest["generated_root"] = f"{SAFE_OUTPUT_ROOT_LABEL}/"
    manifest["manifest_path"] = MANIFEST_PATH_LABEL
    manifest["output"] = MARKER
    return manifest


@contextmanager
def _safe_writer_v08_root():
    original_root = safe_writer.SAFE_OUTPUT_ROOT
    original_label = safe_writer.SAFE_OUTPUT_ROOT_LABEL
    safe_writer.SAFE_OUTPUT_ROOT = SAFE_OUTPUT_ROOT
    safe_writer.SAFE_OUTPUT_ROOT_LABEL = SAFE_OUTPUT_ROOT_LABEL
    try:
        yield
    finally:
        safe_writer.SAFE_OUTPUT_ROOT = original_root
        safe_writer.SAFE_OUTPUT_ROOT_LABEL = original_label


def _write_v08_text_file(path: object, text: object, *, approval: bool) -> dict:
    path_ok, relative_path, path_reason = safe_relative_path(path)
    if not path_ok:
        metadata = _base_metadata(
            decision="blocked",
            reason=path_reason,
            written=False,
            success=False,
        )
        metadata.update({
            "writer_marker": safe_writer.MARKER,
            "path": str(path),
        })
        return metadata

    guard_metadata = guard.guard_decision(WRITE_ACTION)
    if guard_metadata.get("decision") != guard.DECISION_NEEDS_APPROVAL:
        metadata = _base_metadata(
            decision="blocked",
            reason="Write action did not receive guard approval metadata.",
            written=False,
            success=False,
        )
        metadata.update({
            "guard_decision": guard_metadata.get("decision"),
            "path": relative_path,
        })
        return metadata

    with _safe_writer_v08_root():
        metadata = safe_writer.write_safe_text_file(
            relative_path,
            text,
            approval=approval,
            action=WRITE_ACTION,
        )

    metadata.update({
        "builder_marker": MARKER,
        "builder_mode": MODE,
        "builder_safe_output_root": f"{SAFE_OUTPUT_ROOT_LABEL}/",
        "builder_path_reason": path_reason,
    })
    return metadata


def _manifest_readme(manifest: dict) -> str:
    return "\n".join([
        "# NovaKutty UI Manifest",
        "",
        f"Marker: {MARKER}",
        "",
        "This directory contains safe QBIT NOVA UI manifest metadata only.",
        "",
        f"App: {manifest.get('app_name')}",
        f"Manifest: {MANIFEST_PATH_LABEL}",
        "",
        "No app source is generated in this stage.",
        "No existing UI files are edited in this stage.",
        "",
    ])


def generate_ui_manifest_files(*, approval: bool = True, include_readme: bool = True) -> dict:
    manifest = build_ui_manifest()
    validation = validate_ui_manifest(manifest)
    if validation.get("decision") != "allowed":
        return validation

    manifest_text = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    files = [
        _write_v08_text_file(MANIFEST_RELATIVE_PATH, manifest_text, approval=approval),
    ]

    if include_readme:
        files.append(
            _write_v08_text_file(
                README_RELATIVE_PATH,
                _manifest_readme(manifest),
                approval=approval,
            )
        )

    written = all(item.get("written") is True for item in files)
    decision = "success" if written else "needs_approval"
    reason = "Safe UI manifest files written under the v0.8 generated output root."
    if not written:
        reason = "Safe UI manifest files require explicit approval."

    result = _base_metadata(
        decision=decision,
        reason=reason,
        manifest=manifest,
        written=written,
        success=written,
    )
    result.update({
        "mode": MODE,
        "approval_required": True,
        "readme_path": README_PATH_LABEL if include_readme else "",
        "manifest": manifest,
        "files": files,
    })
    return result


def plan_metadata() -> dict:
    manifest = build_ui_manifest()
    metadata = _base_metadata(
        decision="plan",
        reason="Plan only; no files written.",
        manifest=manifest,
        written=False,
        success=True,
    )
    metadata.update({
        "approval_required": False,
        "allowed_component_types": ALLOWED_COMPONENT_TYPES,
        "allowed_action_types": ALLOWED_ACTION_TYPES,
        "guard_write_decision": guard.guard_decision(WRITE_ACTION).get("decision"),
        "write_action": WRITE_ACTION,
        "manifest": manifest,
    })
    return metadata


def _print_result(result: dict) -> None:
    print(MARKER)
    print(json.dumps(result, indent=2, ensure_ascii=False))


def main(argv: list[str]) -> int:
    command = argv[0] if argv else "plan"

    if command == "plan":
        _print_result(plan_metadata())
        return 0

    if command == "demo":
        result = generate_ui_manifest_files(approval=True, include_readme=True)
        _print_result(result)
        if result.get("success") is True:
            print(f"{MARKER}_GREEN")
            return 0
        return 1

    print("Usage: qbit_nova_ui_manifest_builder_v08.py plan|demo")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
