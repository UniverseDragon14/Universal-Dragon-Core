#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import qbit_nova_tokenizer_v01 as tokenizer
import qbit_nova_parser_v01 as parser
import qbit_nova_ast_v01 as qast_tool
import qbit_nova_ir_v01 as qir_tool
import qbit_nova_qbc_v01 as qbc_tool
import qbit_nova_qbc_runner_v01 as runner_tool


def run_full_pipeline(source: str):
    tokens = tokenizer.tokenize(source)
    parsed = parser.parse_source(source)
    qast = qast_tool.build_qast(source)
    qir = qir_tool.build_ir(source)
    qbc = qbc_tool.build_qbc(source)
    run = runner_tool.QBCRunner().run(qbc)

    return {
        "marker": "QBIT_NOVA_FULL_RUNNER_V01",
        "type": "QBITFullRun",
        "mode": "SAFE_PIPELINE_SIMULATION",
        "success": True,
        "counts": {
            "tokens": len(tokens),
            "parser_nodes": len(parsed.get("body", [])),
            "qast_nodes": qast.get("summary", {}).get("node_count", 0),
            "qir_instructions": qir.get("instruction_count", 0),
            "qbc_instructions": qbc.get("instruction_count", 0),
            "runner_trace": len(run.get("trace", [])),
        },
        "output": run.get("output"),
        "state": run.get("state", {}),
    }


def main(argv):
    if len(argv) != 2:
        print("Usage: qbit_nova_run_v01.py <file.qnova|file.ud>")
        return 2

    path = Path(argv[1])
    if not path.exists():
        print(f"File not found: {path}")
        return 1

    result = run_full_pipeline(path.read_text(encoding="utf-8"))

    print("QBIT_NOVA_FULL_RUNNER_V01")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("QBIT_NOVA_FULL_RUNNER_V01_GREEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
