#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from copy import deepcopy

MARKER = "QBIT_NOVA_CORE_ACTION_LIBRARY_V05"
VERSION = "0.5.0"

CORE_ACTIONS = {
    "check": {
        "name": "check",
        "category": "inspection",
        "safe_stage": True,
        "os_execution": False,
        "delete_action": False,
        "description": "Inspect or confirm QBIT NOVA state before continuing.",
    },
    "backup": {
        "name": "backup",
        "category": "preservation",
        "safe_stage": True,
        "os_execution": False,
        "delete_action": False,
        "description": "Preserve safe QBIT NOVA state before later stages.",
    },
    "validate": {
        "name": "validate",
        "category": "verification",
        "safe_stage": True,
        "os_execution": False,
        "delete_action": False,
        "description": "Verify QBIT NOVA source, bytecode, manifest, or metadata meaning.",
    },
    "rollback": {
        "name": "rollback",
        "category": "recovery",
        "safe_stage": True,
        "os_execution": False,
        "delete_action": False,
        "description": "Return to a safe prior QBIT NOVA state if validation fails.",
    },
    "learn": {
        "name": "learn",
        "category": "memory",
        "safe_stage": True,
        "os_execution": False,
        "delete_action": False,
        "description": "Record safe language/core meaning for future QBIT NOVA reasoning.",
    },
    "emit": {
        "name": "emit",
        "category": "output",
        "safe_stage": True,
        "os_execution": False,
        "delete_action": False,
        "description": "Produce QBIT NOVA output text or markers.",
    },
}


def normalize_action_name(name: object) -> str:
    return str(name or "").strip().lower()


def known_action_names() -> tuple[str, ...]:
    return tuple(CORE_ACTIONS)


def known_actions() -> dict[str, dict]:
    return deepcopy(CORE_ACTIONS)


def unknown_action_metadata(name: object) -> dict:
    requested = str(name or "").strip()
    normalized = normalize_action_name(name)
    return {
        "name": normalized,
        "requested_action": requested,
        "category": "unknown",
        "safe_stage": True,
        "os_execution": False,
        "delete_action": False,
        "description": "Unknown QBIT NOVA core action rejected safely.",
        "known": False,
        "allowed": False,
        "success": False,
        "error": "UNKNOWN_QBIT_NOVA_CORE_ACTION",
        "marker": MARKER,
    }


def action_metadata(name: object) -> dict:
    normalized = normalize_action_name(name)
    if normalized not in CORE_ACTIONS:
        return unknown_action_metadata(name)

    meta = deepcopy(CORE_ACTIONS[normalized])
    meta.update({
        "known": True,
        "allowed": True,
        "success": True,
        "marker": MARKER,
    })
    return meta


def action_library() -> dict:
    return {
        "marker": MARKER,
        "version": VERSION,
        "type": "QBITNovaCoreActionLibrary",
        "mode": "SAFE_QBIT_ACTION_MEANING_LIBRARY",
        "safe_stage": True,
        "os_execution": False,
        "delete_action": False,
        "actions": [action_metadata(name) for name in known_action_names()],
        "unknown_action_policy": "return_safe_error_metadata",
        "output": MARKER,
    }


def main(argv: list[str]) -> int:
    if len(argv) > 1:
        print("Usage: qbit_nova_core_actions_v05.py [action]")
        return 2

    result = action_metadata(argv[0]) if argv else action_library()
    print(MARKER)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result.get("success", True) is not False else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
