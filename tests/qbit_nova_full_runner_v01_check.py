#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
SRC = ROOT / "examples" / "v2" / "qbit_nova_full_runner_v01.qnova"
DOC = ROOT / "docs" / "QBIT_NOVA_FULL_RUNNER_V0_1.md"

if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import qbit_nova_run_v01 as run_tool

for p in [SRC, DOC, TOOLS / "qbit_nova_run_v01.py"]:
    if not p.exists():
        raise SystemExit(f"MISSING: {p}")

result = run_tool.run_full_pipeline(SRC.read_text(encoding="utf-8"))

if result.get("marker") != "QBIT_NOVA_FULL_RUNNER_V01":
    raise SystemExit("MISSING FULL RUNNER MARKER")

if result.get("mode") != "SAFE_PIPELINE_SIMULATION":
    raise SystemExit("BAD MODE")

if result.get("output") != "QBIT_NOVA_FULL_RUNNER_V01":
    raise SystemExit("BAD OUTPUT")

counts = result.get("counts", {})
for key in ["tokens", "parser_nodes", "qast_nodes", "qir_instructions", "qbc_instructions", "runner_trace"]:
    if counts.get(key, 0) <= 0:
        raise SystemExit(f"BAD COUNT: {key}")

state = result.get("state", {})
if state.get("qbits", {}).get("intent") != "safe_patch":
    raise SystemExit("MISSING intent=safe_patch")

print("QBIT_NOVA_FULL_RUNNER_V01_GREEN")
