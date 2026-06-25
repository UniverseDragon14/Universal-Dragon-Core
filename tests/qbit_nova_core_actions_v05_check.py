#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
DOC = ROOT / "docs" / "QBIT_NOVA_CORE_ACTION_LIBRARY_V0_5.md"
SRC = ROOT / "examples" / "v2" / "core_actions_v05.qn"
QNOVA = TOOLS / "qnova"
OUT = ROOT / ".tmp" / "core-actions-v05" / "core_actions_v05.qbc"

if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import qbit_nova_core_actions_v05 as core_actions

EXPECTED_ACTIONS = ("check", "backup", "validate", "rollback", "learn", "emit")

for p in [DOC, SRC, QNOVA, TOOLS / "qbit_nova_core_actions_v05.py"]:
    if not p.exists():
        raise SystemExit(f"MISSING: {p}")

doc = DOC.read_text(encoding="utf-8")
for marker in [
    "QBIT_NOVA_CORE_ACTION_LIBRARY_V05",
    "This is not OS execution",
    "This is not real install",
    "This is not delete",
    "No unknown action should silently pass",
    "Unknown action handling must not execute anything",
    "safe_stage: true",
    "os_execution: false",
    "delete_action: false",
    "./tools/qnova run examples/v2/core_actions_v05.qn",
    "Generated QBC must not contain FF opcode",
]:
    if marker not in doc:
        raise SystemExit(f"MISSING DOC MARKER: {marker}")

for name in EXPECTED_ACTIONS:
    if name not in doc:
        raise SystemExit(f"MISSING DOC ACTION: {name}")

library = core_actions.action_library()
if library.get("marker") != "QBIT_NOVA_CORE_ACTION_LIBRARY_V05":
    raise SystemExit("BAD LIBRARY MARKER")

if library.get("mode") != "SAFE_QBIT_ACTION_MEANING_LIBRARY":
    raise SystemExit("BAD LIBRARY MODE")

if library.get("os_execution") is not False:
    raise SystemExit("LIBRARY OS EXECUTION MUST BE FALSE")

if library.get("delete_action") is not False:
    raise SystemExit("LIBRARY DELETE ACTION MUST BE FALSE")

if core_actions.known_action_names() != EXPECTED_ACTIONS:
    raise SystemExit(f"BAD ACTION ORDER: {core_actions.known_action_names()}")

seen = {item.get("name"): item for item in library.get("actions", [])}
if set(seen) != set(EXPECTED_ACTIONS):
    raise SystemExit(f"BAD ACTION SET: {sorted(seen)}")

for name in EXPECTED_ACTIONS:
    meta = core_actions.action_metadata(name)
    required = {
        "name": name,
        "safe_stage": True,
        "os_execution": False,
        "delete_action": False,
        "known": True,
        "allowed": True,
        "success": True,
    }
    for key, expected in required.items():
        if meta.get(key) != expected:
            raise SystemExit(f"BAD {name} {key}: {meta.get(key)}")
    if not meta.get("category"):
        raise SystemExit(f"MISSING CATEGORY: {name}")
    if not meta.get("description"):
        raise SystemExit(f"MISSING DESCRIPTION: {name}")

unknown = core_actions.action_metadata("install")
for key, expected in {
    "category": "unknown",
    "safe_stage": True,
    "os_execution": False,
    "delete_action": False,
    "known": False,
    "allowed": False,
    "success": False,
    "error": "UNKNOWN_QBIT_NOVA_CORE_ACTION",
}.items():
    if unknown.get(key) != expected:
        raise SystemExit(f"BAD UNKNOWN {key}: {unknown.get(key)}")

result = subprocess.run(
    [str(QNOVA), "run", str(SRC), str(OUT)],
    cwd=str(ROOT),
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
)

if result.returncode != 0:
    print(result.stdout)
    raise SystemExit("CORE ACTION SOURCE RUN FAILED")

for marker in [
    "QBIT_NOVA_QNOVA_RUN_COMMAND_V03_GREEN",
    "QBIT_NOVA_CORE_ACTION_LIBRARY_V05",
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

print("QBIT_NOVA_CORE_ACTION_LIBRARY_V05_GREEN")
