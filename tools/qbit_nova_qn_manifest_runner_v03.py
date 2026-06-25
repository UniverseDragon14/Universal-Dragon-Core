#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import qbit_nova_qbc_file_runner_v03 as qbc_file_runner


def run_manifest(source_path: Path, output_path: Path):
    if not source_path.exists():
        raise FileNotFoundError(f"Missing source file: {source_path}")

    if source_path.suffix not in {".qn", ".qnova", ".ud"}:
        raise ValueError(f"Unsupported QBIT source extension: {source_path.suffix}")

    result = qbc_file_runner.run_qbc_file(source_path, output_path)

    if result.get("marker") != "QBIT_NOVA_QBC_FILE_RUNNER_V03":
        raise ValueError("QBC file runner marker mismatch")

    decoded_output = result.get("decoded_output")

    if not isinstance(decoded_output, str) or not decoded_output.startswith("QBIT_NOVA_"):
        raise ValueError(f"Bad decoded output marker: {decoded_output}")

    state = result.get("state", {})
    qbits = state.get("qbits", {})
    meta = state.get("meta", {})

    intent = qbits.get("intent")
    target = qbits.get("target")
    package = qbits.get("package")

    if not intent:
        raise ValueError("Manifest missing q.intent")

    if meta.get("creator") != "aslam":
        raise ValueError("Manifest creator must be aslam")

    qbc_text = Path(result["qbc"]).read_text(encoding="utf-8")
    if "FF" in qbc_text.split():
        raise ValueError("Unknown opcode FF found")

    manifest = {
        "intent": intent,
        "target": target,
        "package": package,
        "output_marker": decoded_output,
        "source_extension": source_path.suffix,
        "safe_stage": True,
        "os_execution": False,
        "delete_action": False,
    }

    if intent.startswith("install") and not package:
        raise ValueError("Install manifest must include q.package")

    if intent.startswith("install") and not target:
        raise ValueError("Install manifest must include q.target")

    return {
        "marker": "QBIT_NOVA_QN_MANIFEST_RUNNER_V03",
        "type": "QNManifestRunner",
        "mode": "SAFE_QN_MANIFEST_READ",
        "success": True,
        "source": str(source_path),
        "qbc": result.get("qbc"),
        "writer_marker": result.get("writer_marker"),
        "loader_marker": result.get("loader_marker"),
        "bytecode_runner_marker": result.get("runner_marker"),
        "decoded_output": decoded_output,
        "manifest": manifest,
        "trace_size": len(result.get("trace", [])),
        "output": "QBIT_NOVA_QN_MANIFEST_RUNNER_V03",
    }


def main(argv):
    if len(argv) != 3:
        print("Usage: qbit_nova_qn_manifest_runner_v03.py <source.qn|source.qnova> <output.qbc>")
        return 2

    source_path = Path(argv[1])
    output_path = Path(argv[2])

    try:
        result = run_manifest(source_path, output_path)
    except Exception as e:
        print("QBIT_NOVA_QN_MANIFEST_RUNNER_V03_ERROR")
        print(str(e))
        return 1

    print("QBIT_NOVA_QN_MANIFEST_RUNNER_V03")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("QBIT_NOVA_QN_MANIFEST_RUNNER_V03_GREEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
