#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import qbit_nova_qbc_file_writer_v03 as writer_tool
import qbit_nova_qbc_file_loader_v03 as loader_tool


def run_qbc_file(source_path: Path, output_path: Path):
    if not source_path.exists():
        raise FileNotFoundError(f"Missing source file: {source_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    write_result = writer_tool.write_qbc_file(source_path, output_path)

    if write_result.get("marker") != "QBIT_NOVA_QBC_FILE_WRITER_V03":
        raise ValueError("Writer marker mismatch")

    qbc_text = output_path.read_text(encoding="utf-8").strip()
    qbc_stream = qbc_text.split() if qbc_text else []

    if "FF" in qbc_stream:
        raise ValueError("Unknown opcode FF found after writer stage")

    load_result = loader_tool.load_qbc_files(output_path)

    if load_result.get("marker") != "QBIT_NOVA_QBC_FILE_LOADER_V03":
        raise ValueError("Loader marker mismatch")

    if load_result.get("runner_marker") != "QBIT_NOVA_QBC_RUNNER_V01":
        raise ValueError("QBC runner marker mismatch")

    if load_result.get("runner_mode") != "SAFE_BYTECODE_SIMULATION":
        raise ValueError("QBC runner mode mismatch")

    expected_output = "QBIT_NOVA_QBC_FILE_RUNNER_V03"

    if load_result.get("decoded_output") != expected_output:
        raise ValueError(
            f"Decoded output mismatch: expected {expected_output}, got {load_result.get('decoded_output')}"
        )

    return {
        "marker": "QBIT_NOVA_QBC_FILE_RUNNER_V03",
        "type": "QBCFileRunner",
        "mode": "SAFE_QBC_FILE_RUN",
        "success": True,
        "source": str(source_path),
        "qbc": str(output_path),
        "json": write_result.get("json"),
        "pool": write_result.get("pool"),
        "expanded": write_result.get("expanded"),
        "writer_marker": write_result.get("marker"),
        "loader_marker": load_result.get("marker"),
        "runner_marker": load_result.get("runner_marker"),
        "runner_mode": load_result.get("runner_mode"),
        "decoded_output": load_result.get("decoded_output"),
        "instruction_count": load_result.get("instruction_count"),
        "stream_size": load_result.get("stream_size"),
        "state": load_result.get("state", {}),
        "trace": load_result.get("trace", []),
        "output": expected_output,
    }


def main(argv):
    if len(argv) != 3:
        print("Usage: qbit_nova_qbc_file_runner_v03.py <source.qnova|source.ud> <output.qbc>")
        return 2

    source_path = Path(argv[1])
    output_path = Path(argv[2])

    try:
        result = run_qbc_file(source_path, output_path)
    except Exception as e:
        print("QBIT_NOVA_QBC_FILE_RUNNER_V03_ERROR")
        print(str(e))
        return 1

    print("QBIT_NOVA_QBC_FILE_RUNNER_V03")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("QBIT_NOVA_QBC_FILE_RUNNER_V03_GREEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
