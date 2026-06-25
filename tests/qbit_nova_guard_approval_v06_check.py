#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
DOC = ROOT / "docs" / "QBIT_NOVA_GUARD_APPROVAL_ENGINE_V0_6.md"
SRC = ROOT / "examples" / "v2" / "guard_approval_v06.qn"
QNOVA = TOOLS / "qnova"
OUT = ROOT / ".tmp" / "guard-approval-v06" / "guard_approval_v06.qbc"

if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import qbit_nova_core_actions_v05 as core_actions
import qbit_nova_guard_approval_v06 as guard

MARKER = "QBIT_NOVA_GUARD_APPROVAL_ENGINE_V06"
ALLOWED_ACTIONS = ("check", "backup", "validate", "rollback", "learn", "emit")
APPROVAL_ACTIONS = ("install", "write_file", "network")
BLOCKED_ACTIONS = ("delete", "remove", "rmdir", "secret", "token")

for p in [DOC, SRC, QNOVA, TOOLS / "qbit_nova_guard_approval_v06.py", TOOLS / "qbit_nova_core_actions_v05.py"]:
    if not p.exists():
        raise SystemExit(f"MISSING: {p}")

doc = DOC.read_text(encoding="utf-8")
for marker in [
    MARKER,
    "tools/qbit_nova_core_actions_v05.py",
    "safety and approval layer only",
    "This is not OS execution",
    "This is not real install",
    "This is not delete",
    "unknown action",
    "decision: allowed / needs_approval / blocked",
    "safe_stage: true",
    "os_execution: false",
    "delete_action: false",
    "./tools/qnova run examples/v2/guard_approval_v06.qn",
    "Generated QBC must not contain standalone FF opcode",
]:
    if marker not in doc:
        raise SystemExit(f"MISSING DOC MARKER: {marker}")

for name in [*ALLOWED_ACTIONS, *APPROVAL_ACTIONS, *BLOCKED_ACTIONS]:
    if name not in doc:
        raise SystemExit(f"MISSING DOC ACTION: {name}")

if guard.MARKER != MARKER:
    raise SystemExit("BAD GUARD MARKER")

if guard.allowed_action_names() != core_actions.known_action_names():
    raise SystemExit("GUARD MUST USE CORE ACTION LIBRARY ORDER")

policy = guard.guard_policy()
for key, expected in {
    "marker": MARKER,
    "version": "0.6.0",
    "mode": "SAFE_QBIT_NOVA_GUARD_APPROVAL_ONLY",
    "safe_stage": True,
    "os_execution": False,
    "delete_action": False,
    "core_action_library": core_actions.MARKER,
    "unknown_action_decision": "blocked",
}.items():
    if policy.get(key) != expected:
        raise SystemExit(f"BAD POLICY {key}: {policy.get(key)}")

if tuple(policy.get("allowed_actions", ())) != ALLOWED_ACTIONS:
    raise SystemExit(f"BAD ALLOWED ACTIONS: {policy.get('allowed_actions')}")

if tuple(policy.get("approval_actions", ())) != APPROVAL_ACTIONS:
    raise SystemExit(f"BAD APPROVAL ACTIONS: {policy.get('approval_actions')}")

if tuple(policy.get("blocked_actions", ())) != BLOCKED_ACTIONS:
    raise SystemExit(f"BAD BLOCKED ACTIONS: {policy.get('blocked_actions')}")


def assert_decision(action: str, decision: str) -> None:
    metadata = guard.guard_decision(action)
    required = {
        "action": action,
        "decision": decision,
        "safe_stage": True,
        "os_execution": False,
        "delete_action": False,
        "marker": MARKER,
        "version": "0.6.0",
    }
    for key, expected in required.items():
        if metadata.get(key) != expected:
            raise SystemExit(f"BAD {action} {key}: {metadata.get(key)}")
    if not metadata.get("reason"):
        raise SystemExit(f"MISSING REASON: {action}")


for action in ALLOWED_ACTIONS:
    assert_decision(action, "allowed")
    metadata = guard.guard_decision(action)
    if metadata.get("core_marker") != core_actions.MARKER:
        raise SystemExit(f"MISSING CORE MARKER: {action}")
    if metadata.get("core_known") is not True:
        raise SystemExit(f"CORE ACTION NOT KNOWN: {action}")

for action in APPROVAL_ACTIONS:
    assert_decision(action, "needs_approval")

for action in BLOCKED_ACTIONS:
    assert_decision(action, "blocked")

unknown = guard.guard_decision("format_disk")
for key, expected in {
    "action": "format_disk",
    "decision": "blocked",
    "safe_stage": True,
    "os_execution": False,
    "delete_action": False,
}.items():
    if unknown.get(key) != expected:
        raise SystemExit(f"BAD UNKNOWN {key}: {unknown.get(key)}")

if "Unknown QBIT NOVA action" not in unknown.get("reason", ""):
    raise SystemExit("BAD UNKNOWN REASON")

result = subprocess.run(
    [str(QNOVA), "run", str(SRC), str(OUT)],
    cwd=str(ROOT),
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
)

if result.returncode != 0:
    print(result.stdout)
    raise SystemExit("GUARD APPROVAL SOURCE RUN FAILED")

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

print("QBIT_NOVA_GUARD_APPROVAL_ENGINE_V06_GREEN")
