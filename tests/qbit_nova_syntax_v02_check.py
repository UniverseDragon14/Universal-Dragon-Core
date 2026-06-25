#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
SRC = ROOT / "examples" / "v2" / "qbit_nova_syntax_v02.qnova"
DOC = ROOT / "docs" / "QBIT_NOVA_SYNTAX_V0_2.md"

if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import qbit_nova_syntax_v02 as syntax_tool

for p in [
    TOOLS / "qbit_nova_syntax_v02.py",
    TOOLS / "qbit_nova_run_v01.py",
    SRC,
    DOC,
]:
    if not p.exists():
        raise SystemExit(f"MISSING: {p}")

source = SRC.read_text(encoding="utf-8")
expanded = syntax_tool.expand_source(source)
result = syntax_tool.run_symbolic_source(source)

checks = [
    "qnova v02",
    "brain novakutty",
    "creator aslam",
    "project universal_dragon",
    "team askutty",
    "law qbit_nova_identity_only",
    "qbit intent = safe_patch",
    "guard intent:",
    "    check first",
    "    backup before_change",
    "    validate after_change",
    "    rollback on_fail",
    "    learn always",
    "emit QBIT_NOVA_SYNTAX_V02",
]

for c in checks:
    if c not in expanded:
        raise SystemExit(f"MISSING EXPANSION: {c}")

if result.get("marker") != "QBIT_NOVA_SYNTAX_V02":
    raise SystemExit("MISSING SYNTAX MARKER")

if result.get("mode") != "SAFE_SYMBOLIC_PIPELINE":
    raise SystemExit("BAD SYMBOLIC MODE")

if result.get("output") != "QBIT_NOVA_SYNTAX_V02":
    raise SystemExit("BAD SYMBOLIC OUTPUT")

full = result.get("full_runner", {})
if full.get("marker") != "QBIT_NOVA_FULL_RUNNER_V01":
    raise SystemExit("FULL RUNNER NOT USED")

counts = full.get("counts", {})
for key in ["tokens", "qast_nodes", "qir_instructions", "qbc_instructions", "runner_trace"]:
    if counts.get(key, 0) <= 0:
        raise SystemExit(f"BAD COUNT: {key}")

doc = DOC.read_text(encoding="utf-8")
for marker in [
    "QBIT NOVA Syntax v0.2",
    "@ = identity / header / law",
    "QBIT_NOVA_SYNTAX_V02",
]:
    if marker not in doc:
        raise SystemExit(f"MISSING DOC MARKER: {marker}")

print("QBIT_NOVA_SYNTAX_V02_GREEN")
