#!/usr/bin/env python3
"""Nova Guard adapter for the Carry-On gateway.

Every gateway request is checked here before any action runs. We prefer the
repo's existing approval engine (tools/qbit_nova_guard_approval_v06.py) so the
gateway shares one policy with the rest of QBIT NOVA. If that module cannot be
imported, we fall back to a conservative built-in policy with the same three
decisions, so the gateway is never left un-guarded.

Decisions: "allowed" | "needs_approval" | "blocked".
"""
from __future__ import annotations

import os
import sys

from carryon.common.log import get_logger

MARKER = "CARRYON_GATEWAY_GUARD_V01"
VERSION = "0.1.0"

log = get_logger("gateway.guard")

_TOOLS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "tools")
)

_repo_guard = None
try:
    if _TOOLS_DIR not in sys.path:
        sys.path.insert(0, _TOOLS_DIR)
    import qbit_nova_guard_approval_v06 as _repo_guard  # type: ignore
    log.info("using repo Nova Guard", version=getattr(_repo_guard, "VERSION", "?"))
except Exception as exc:  # fall back to built-in policy
    log.warn("repo Nova Guard unavailable, using built-in policy", error=str(exc))

# Built-in fallback policy mirrors tools/qbit_nova_guard_approval_v06.py.
_APPROVAL = {"install", "write_file", "network"}
_BLOCKED = {"delete", "remove", "rmdir", "secret", "token"}
_ALLOWED = {"check", "backup", "validate", "rollback", "inspect"}


def evaluate(category: str) -> dict:
    """Return {'decision', 'reason'} for a Nova Guard action category."""
    if _repo_guard is not None:
        try:
            meta = _repo_guard.guard_decision(category)  # type: ignore[attr-defined]
            return {"decision": meta.get("decision"), "reason": meta.get("reason")}
        except AttributeError:
            pass  # older/newer API shape; use built-in below
        except Exception as exc:
            log.error("repo guard evaluate failed", error=str(exc))

    if category in _BLOCKED:
        return {"decision": "blocked", "reason": "Destructive/sensitive action blocked by guard policy."}
    if category in _APPROVAL:
        return {"decision": "needs_approval", "reason": "Action can affect the environment and needs approval."}
    if category in _ALLOWED:
        return {"decision": "allowed", "reason": "Known safe Carry-On action."}
    return {"decision": "blocked", "reason": "Unknown action is blocked by guard policy."}
