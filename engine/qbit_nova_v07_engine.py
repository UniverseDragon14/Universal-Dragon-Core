#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

LANGUAGE = "QBIT NOVA"
UD = "Universal Dragon"
CREATOR = "Aslam"
TEAM = "Askutty"
BRAIN = "NovaKutty"
VERSION = "v0.7-native-engine"

REQUIRED_ADAPTER = [
    "mode safe_reply",
    "owner_approval required",
    "risky_action deny",
]

def clean_value(v):
    v = str(v or "").strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in ["'", '"']:
        return v[1:-1]
    return v

def identity(kind, value):
    value = clean_value(value).strip()
    table = {
        "creator": ("aslam", "Aslam"),
        "team": ("askutty", "Askutty"),
        "brain": ("novakutty", "NovaKutty"),
    }
    low, proper = table.get(kind, ("", value))
    return proper if value.lower() == low else value

def parse_ud(path):
    lines = Path(path).read_text(encoding="utf-8").splitlines()

    ast = {
        "language": LANGUAGE,
        "version": VERSION,
        "ud": UD,
        "source": str(path),
        "nova": "",
        "creator": "Unknown",
        "team": "Unknown",
        "brain": "Unknown",
        "memory": [],
        "qbits": [],
        "measurements": [],
        "says": [],
        "when_blocks": [],
        "adapters": [],
        "runtime": [],
    }

    i = 0
    while i < len(lines):
        raw = lines[i]
        line = raw.strip()
        low = line.lower()

        if not line or line.startswith("#"):
            i += 1
            continue

        if low.startswith("nova "):
            ast["nova"] = line.split(None, 1)[1].strip()
            i += 1
            continue

        if low.startswith("creator "):
            ast["creator"] = identity("creator", line.split(None, 1)[1])
            i += 1
            continue

        if low.startswith("team "):
            ast["team"] = identity("team", line.split(None, 1)[1])
            i += 1
            continue

        if low.startswith("brain "):
            ast["brain"] = identity("brain", line.split(None, 1)[1])
            i += 1
            continue

        if low.startswith("memory ") and "=" in line:
            left, right = line[len("memory "):].split("=", 1)
            ast["memory"].append({
                "name": left.strip(),
                "value": clean_value(right),
            })
            i += 1
            continue

        if low.startswith("say "):
            ast["says"].append(clean_value(line[4:]))
            i += 1
            continue

        m = re.match(r"qbit\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(\|[^>]+>)", line)
        if m:
            ast["qbits"].append({
                "name": m.group(1),
                "state": m.group(2),
            })
            i += 1
            continue

        if low.startswith("measure "):
            ast["measurements"].append({
                "target": line.split(None, 1)[1].strip(),
            })
            i += 1
            continue

        if low.startswith("runtime "):
            ast["runtime"].append(line.split(None, 1)[1].strip())
            i += 1
            continue

        if low.startswith("when "):
            condition = line.rstrip(":")[len("when "):].strip()
            body = []
            i += 1
            while i < len(lines):
                body_raw = lines[i]
                body_line = body_raw.strip()
                if body_line and not (body_raw.startswith(" ") or body_raw.startswith("\t")):
                    break
                if body_line:
                    body.append(body_line)
                i += 1
            ast["when_blocks"].append({
                "condition": condition,
                "body": body,
            })
            continue

        if low.startswith("adapter "):
            name = line[len("adapter "):].rstrip(":").strip()
            body = []
            i += 1
            while i < len(lines):
                body_raw = lines[i]
                body_line = body_raw.strip()
                if body_line and not (body_raw.startswith(" ") or body_raw.startswith("\t")):
                    break
                if body_line:
                    body.append(body_line)
                i += 1
            ast["adapters"].append({
                "name": name,
                "body": body,
            })
            continue

        i += 1

    return ast

def semantic_errors(ast):
    errors = []

    if ast.get("creator") != CREATOR:
        errors.append("creator must be Aslam")
    if ast.get("team") != TEAM:
        errors.append("team must be Askutty")
    if ast.get("brain") != BRAIN:
        errors.append("brain must be NovaKutty")

    qbits = {q["name"]: q["state"] for q in ast.get("qbits", [])}
    measured = {m["target"] for m in ast.get("measurements", [])}

    for name, state in qbits.items():
        if state not in ["|0>", "|1>"]:
            errors.append("qbit " + name + " has invalid state " + state)

    for block in ast.get("when_blocks", []):
        condition = block.get("condition", "")
        m = re.match(r"([A-Za-z_][A-Za-z0-9_]*)\s*==\s*([01])", condition)
        if not m:
            errors.append("invalid when condition: " + condition)
            continue

        qname = m.group(1)
        if qname not in qbits:
            errors.append("when qbit " + qname + " is not declared")
        if qname not in measured:
            errors.append("when qbit " + qname + " must be measured before branch")

    for adapter in ast.get("adapters", []):
        if adapter.get("name") == "whatsapp":
            body = [x.strip() for x in adapter.get("body", [])]
            for item in REQUIRED_ADAPTER:
                if item not in body:
                    errors.append("adapter whatsapp missing: " + item)

    return errors

def compile_ir(ast):
    ir = [
        "ID\tLANGUAGE\t" + LANGUAGE,
        "ID\tUD\t" + UD,
        "ID\tCREATOR\t" + ast.get("creator", ""),
        "ID\tTEAM\t" + ast.get("team", ""),
        "ID\tBRAIN\t" + ast.get("brain", ""),
    ]

    for item in ast.get("memory", []):
        ir.append("MEM\t" + item["name"] + "\t" + item["value"])

    for text in ast.get("says", []):
        ir.append("SAY\t" + text)

    for q in ast.get("qbits", []):
        ir.append("QBIT\t" + q["name"] + "\t" + q["state"])

    for item in ast.get("measurements", []):
        ir.append("MEASURE\t" + item["target"])

    for block in ast.get("when_blocks", []):
        ir.append("BRANCH\t" + block["condition"])
        for body in block.get("body", []):
            ir.append("BODY\t" + body)

    for adapter in ast.get("adapters", []):
        ir.append("ADAPTER\t" + adapter["name"])
        for body in adapter.get("body", []):
            ir.append("ADAPTER_BODY\t" + body)

    for runtime in ast.get("runtime", []):
        ir.append("RUNTIME\t" + runtime)

    return ir

def qbit_result(state):
    return "1" if state == "|1>" else "0"

def run_qvm(ast):
    out = []
    states = {q["name"]: q["state"] for q in ast.get("qbits", [])}
    measured = {}

    out.append("QVM runtime online")
    out.append("language: " + LANGUAGE)
    out.append("creator: " + ast.get("creator", ""))
    out.append("team: " + ast.get("team", ""))
    out.append("brain: " + ast.get("brain", ""))

    for text in ast.get("says", []):
        out.append(text)

    for name, state in states.items():
        out.append("qbit " + name + " = " + state)

    for item in ast.get("measurements", []):
        target = item["target"]
        result = qbit_result(states.get(target, "|0>"))
        measured[target] = result
        out.append("measure " + target + " => " + result)

    for block in ast.get("when_blocks", []):
        m = re.match(r"([A-Za-z_][A-Za-z0-9_]*)\s*==\s*([01])", block.get("condition", ""))
        if not m:
            continue

        qname = m.group(1)
        expected = m.group(2)

        if measured.get(qname) == expected:
            out.append("when " + qname + " == " + expected + " selected")
            for body in block.get("body", []):
                if body.startswith("say "):
                    out.append(clean_value(body[4:]))
                else:
                    out.append(body)

    for adapter in ast.get("adapters", []):
        out.append("adapter " + adapter.get("name", "") + " contract loaded")
        for body in adapter.get("body", []):
            out.append(body)

    return out

def cmd_ast(ast):
    print(json.dumps(ast, indent=2))
    return 0

def cmd_check(ast):
    errors = semantic_errors(ast)

    print("QBIT NOVA v0.7 semantic check")
    print("source: " + ast.get("source", ""))
    print("creator: " + ast.get("creator", ""))
    print("team: " + ast.get("team", ""))
    print("brain: " + ast.get("brain", ""))
    print("qbits: " + str(len(ast.get("qbits", []))))
    print("measurements: " + str(len(ast.get("measurements", []))))
    print("when_blocks: " + str(len(ast.get("when_blocks", []))))
    print("adapters: " + str(len(ast.get("adapters", []))))

    if errors:
        print("semantic status: RED")
        for err in errors:
            print("- " + err)
        print("QBIT_NOVA_V07_SEMANTIC_RED")
        return 1

    print("semantic status: GREEN")
    print("QBIT_NOVA_V07_SEMANTIC_GREEN")
    return 0

def cmd_compile(ast):
    errors = semantic_errors(ast)
    if errors:
        for err in errors:
            print("RED: " + err)
        return 1

    print("QBIT_IR_BEGIN")
    for line in compile_ir(ast):
        print(line)
    print("QBIT_IR_END")
    return 0

def cmd_run(ast):
    errors = semantic_errors(ast)
    if errors:
        print("QBIT NOVA v0.7 native engine RED")
        for err in errors:
            print("- " + err)
        print("QBIT_NOVA_V07_NATIVE_ENGINE_RED")
        return 1

    print("QBIT NOVA v0.7 native engine online")
    print("source: " + ast.get("source", ""))
    print("compile path: UD_SOURCE -> AST -> QBIT_IR -> QVM")

    print("QBIT_IR_BEGIN")
    for line in compile_ir(ast):
        print(line)
    print("QBIT_IR_END")

    print("QVM_RUN_BEGIN")
    for line in run_qvm(ast):
        print(line)
    print("QVM_RUN_END")

    print("QBIT_NOVA_V07_NATIVE_ENGINE_GREEN")
    return 0

def main():
    if len(sys.argv) < 3:
        print("Usage: qbit_nova_v07_engine.py <ast|check|compile|run> <file.ud>")
        return 1

    command = sys.argv[1]
    source = Path(sys.argv[2])

    if not source.exists():
        print("QBIT NOVA file not found: " + str(source))
        return 1

    ast = parse_ud(source)

    if command == "ast":
        return cmd_ast(ast)
    if command == "check":
        return cmd_check(ast)
    if command == "compile":
        return cmd_compile(ast)
    if command == "run":
        return cmd_run(ast)

    print("Unknown command: " + command)
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
