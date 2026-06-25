#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import qbit_nova_run_v01 as full_runner


def expand_symbolic_line(line: str) -> str:
    raw = line.strip()

    if not raw:
        return ""

    if raw.startswith("#"):
        return ""

    if raw.startswith("@"):
        body = raw[1:]
        if "." not in body:
            return body

        key, value = body.split(".", 1)

        if key == "nova":
            return f"qnova {value}"

        if key == "law":
            return f"law {value}"

        return f"{key} {value}"

    if raw.startswith("q."):
        parts = raw.split(".")
        if len(parts) >= 3:
            name = parts[1]
            value = ".".join(parts[2:])
            return f"qbit {name} = {value}"
        return "qbit"

    if raw.startswith("g.") and raw.endswith(":"):
        body = raw[2:-1]
        return f"guard {body}:"

    if raw.startswith("?"):
        body = raw[1:].strip()
        if "." in body:
            a, b = body.split(".", 1)
            return f"    {a} {b}"
        return f"    check {body}"

    if raw.startswith("+"):
        body = raw[1:].strip()
        if "." in body:
            a, b = body.split(".", 1)
            return f"    {a} {b}"
        return f"    action {body}"

    if raw.startswith("!"):
        body = raw[1:].strip()
        if "." in body:
            a, b = body.split(".", 1)
            return f"    {a} {b}"
        return f"    rollback {body}"

    if raw.startswith(">"):
        return "emit " + raw[1:].strip()

    return raw


def expand_source(source: str) -> str:
    lines = []
    for line in source.splitlines():
        expanded = expand_symbolic_line(line)
        if expanded:
            lines.append(expanded)
    return "\n".join(lines) + "\n"


def run_symbolic_source(source: str):
    expanded = expand_source(source)
    result = full_runner.run_full_pipeline(expanded)
    return {
        "marker": "QBIT_NOVA_SYNTAX_V02",
        "type": "QBITSymbolicRun",
        "mode": "SAFE_SYMBOLIC_PIPELINE",
        "success": True,
        "expanded_source": expanded,
        "full_runner": result,
        "output": result.get("output"),
    }


def main(argv):
    if len(argv) != 2:
        print("Usage: qbit_nova_syntax_v02.py <file.qnova|file.ud>")
        return 2

    path = Path(argv[1])
    if not path.exists():
        print(f"File not found: {path}")
        return 1

    result = run_symbolic_source(path.read_text(encoding="utf-8"))

    print("QBIT_NOVA_SYNTAX_V02")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("QBIT_NOVA_SYNTAX_V02_GREEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
