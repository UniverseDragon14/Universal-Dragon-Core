#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import qbit_nova_qbc_runner_v01 as runner_tool


def read_json(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_qbc_files(qbc_path: Path):
    if not qbc_path.exists():
        raise FileNotFoundError(f"Missing QBC file: {qbc_path}")

    json_path = qbc_path.with_suffix(qbc_path.suffix + ".json")
    pool_path = qbc_path.with_suffix(qbc_path.suffix + ".pool.json")

    qbc_text = qbc_path.read_text(encoding="utf-8").strip()
    qbc_stream = qbc_text.split() if qbc_text else []

    qbc_json = read_json(json_path)
    pool_json = read_json(pool_path)

    if qbc_json.get("marker") != "QBIT_NOVA_QBC_V01":
        raise ValueError("Bad QBC JSON marker")

    if qbc_json.get("arg_pool") != pool_json:
        raise ValueError("Pool JSON does not match QBC JSON arg_pool")

    if qbc_json.get("compact_stream") != qbc_stream:
        raise ValueError("QBC stream does not match QBC JSON compact_stream")

    if "FF" in qbc_stream:
        raise ValueError("Unknown opcode FF found in QBC stream")

    run = runner_tool.QBCRunner().run(qbc_json)

    return {
        "marker": "QBIT_NOVA_QBC_FILE_LOADER_V03",
        "type": "QBCFileLoad",
        "mode": "SAFE_BYTECODE_FILE_LOAD",
        "success": True,
        "qbc": str(qbc_path),
        "json": str(json_path),
        "pool": str(pool_path),
        "instruction_count": qbc_json.get("instruction_count", 0),
        "stream_size": len(qbc_stream),
        "decoded_output": run.get("output"),
        "runner_marker": run.get("marker"),
        "runner_mode": run.get("mode"),
        "state": run.get("state", {}),
        "trace": run.get("trace", []),
        "output": "QBIT_NOVA_QBC_FILE_LOADER_V03",
    }


def main(argv):
    if len(argv) != 2:
        print("Usage: qbit_nova_qbc_file_loader_v03.py <input.qbc>")
        return 2

    qbc_path = Path(argv[1])

    try:
        result = load_qbc_files(qbc_path)
    except Exception as e:
        print("QBIT_NOVA_QBC_FILE_LOADER_V03_ERROR")
        print(str(e))
        return 1

    print("QBIT_NOVA_QBC_FILE_LOADER_V03")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("QBIT_NOVA_QBC_FILE_LOADER_V03_GREEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
