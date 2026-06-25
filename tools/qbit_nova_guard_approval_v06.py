#!/usr/bin/env python3
from __future__ import annotations

import json
import sys

import qbit_nova_core_actions_v05 as core_actions

MARKER = "QBIT_NOVA_GUARD_APPROVAL_ENGINE_V06"
VERSION = "0.6.0"

DECISION_ALLOWED = "allowed"
DECISION_NEEDS_APPROVAL = "needs_approval"
DECISION_BLOCKED = "blocked"

APPROVAL_ACTIONS = ("install", "write_file", "network")
BLOCKED_ACTIONS = ("delete", "remove", "rmdir", "secret", "token")

ALLOWED_REASON = "Known safe QBIT NOVA core action from v0.5 library."
APPROVAL_REASONS = {
    "install": "Action can affect the environment and requires human approval.",
    "write_file": "Action can affect files and requires human approval.",
    "network": "Action can affect external systems and requires human approval.",
}
BLOCKED_REASONS = {
    "delete": "Destructive action is blocked by guard policy.",
    "remove": "Destructive action is blocked by guard policy.",
    "rmdir": "Destructive action is blocked by guard policy.",
    "secret": "Sensitive credential action is blocked by guard policy.",
    "token": "Sensitive credential action is blocked by guard policy.",
}
UNKNOWN_REASON = "Unknown QBIT NOVA action is blocked by guard policy."


def allowed_action_names() -> tuple[str, ...]:
    return core_actions.known_action_names()


def approval_action_names() -> tuple[str, ...]:
    return APPROVAL_ACTIONS


def blocked_action_names() -> tuple[str, ...]:
    return BLOCKED_ACTIONS


def normalize_action_name(name: object) -> str:
    return core_actions.normalize_action_name(name)


def _decision_metadata(action: str, decision: str, reason: str) -> dict:
    return {
        "marker": MARKER,
        "version": VERSION,
        "action": action,
        "decision": decision,
        "safe_stage": True,
        "os_execution": False,
        "delete_action": False,
        "reason": reason,
    }


def guard_decision(name: object) -> dict:
    action = normalize_action_name(name)

    if action in allowed_action_names():
        metadata = _decision_metadata(action, DECISION_ALLOWED, ALLOWED_REASON)
        metadata.update({
            "core_marker": core_actions.MARKER,
            "core_known": core_actions.action_metadata(action).get("known") is True,
        })
        return metadata

    if action in APPROVAL_ACTIONS:
        return _decision_metadata(action, DECISION_NEEDS_APPROVAL, APPROVAL_REASONS[action])

    if action in BLOCKED_ACTIONS:
        return _decision_metadata(action, DECISION_BLOCKED, BLOCKED_REASONS[action])

    return _decision_metadata(action, DECISION_BLOCKED, UNKNOWN_REASON)


def guard_decisions(actions: list[object] | tuple[object, ...]) -> list[dict]:
    return [guard_decision(action) for action in actions]


def guard_policy() -> dict:
    return {
        "marker": MARKER,
        "version": VERSION,
        "type": "QBITNovaGuardApprovalEngine",
        "mode": "SAFE_QBIT_NOVA_GUARD_APPROVAL_ONLY",
        "safe_stage": True,
        "os_execution": False,
        "delete_action": False,
        "core_action_library": core_actions.MARKER,
        "allowed_actions": allowed_action_names(),
        "approval_actions": approval_action_names(),
        "blocked_actions": blocked_action_names(),
        "unknown_action_decision": DECISION_BLOCKED,
        "decisions": guard_decisions([
            *allowed_action_names(),
            *approval_action_names(),
            *blocked_action_names(),
            "unknown_action",
        ]),
        "output": MARKER,
    }


def main(argv: list[str]) -> int:
    if not argv:
        result: dict | list[dict] = guard_policy()
    elif len(argv) == 1:
        result = guard_decision(argv[0])
    else:
        result = guard_decisions(argv)

    print(MARKER)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
