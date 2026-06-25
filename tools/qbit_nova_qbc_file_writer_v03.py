#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import qbit_nova_syntax_v02 as syntax_tool
import qbit_nova_qbc_v01 as qbc_tool


def build_qbc_from_source(source: str):
    expanded = syntax_tool.expand_source(source)
    qbc = qbc_tool.build_qbc(expanded)
    return expanded, qbc


def write_qbc_file(source_path: Path, output_path: Path):
    source = source_path.read_text(encoding="utf-8")
    expanded, qbc = build_qbc_from_source(source)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    stream_text = " ".join(qbc.get("compact_stream", [])) + "\n"
    output_path.write_text(stream_text, encoding="utf-8")

    json_path = output_path.with_suffix(output_path.suffix + ".json")
    pool_path = output_path.with_suffix(output_path.suffix + ".pool.json")
    expanded_path = output_path.with_suffix(output_path.suffix + ".expanded.qnova")

    json_path.write_text(json.dumps(qbc, indent=2, ensure_ascii=False), encoding="utf-8")
    pool_path.write_text(json.dumps(qbc.get("arg_pool", []), indent=2, ensure_ascii=False), encoding="utf-8")
    expanded_path.write_text(expanded, encoding="utf-8")

    return {
        "marker": "QBIT_NOVA_QBC_FILE_WRITER_V03",
        "type": "QBCFileWrite",
        "mode": "SAFE_BYTECODE_FILE_WRITE",
        "success": True,
        "source": str(source_path),
        "qbc": str(output_path),
        "json": str(json_path),
        "pool": str(pool_path),
        "expanded": str(expanded_path),
        "instruction_count": qbc.get("instruction_count", 0),
        "stream_size": len(qbc.get("compact_stream", [])),
        "output": "QBIT_NOVA_QBC_FILE_WRITER_V03",
    }


def main(argv):
    if len(argv) != 3:
        print("Usage: qbit_nova_qbc_file_writer_v03.py <source.qnova|source.ud> <output.qbc>")
        return 2

    source_path = Path(argv[1])
    output_path = Path(argv[2])

    if not source_path.exists():
        print(f"File not found: {source_path}")
        return 1

    result = write_qbc_file(source_path, output_path)

    print("QBIT_NOVA_QBC_FILE_WRITER_V03")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("QBIT_NOVA_QBC_FILE_WRITER_V03_GREEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
