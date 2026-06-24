#!/usr/bin/env python3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE_DIR = ROOT / "engine"
sys.path.insert(0, str(ENGINE_DIR))

import qbit_nova_v07_engine as native
import qbit_nova_v09_token_parser as token_parser

def normalize_ast(ast):
    # Keep v0.9 token parser output compatible with QVM.
    for block in ast.get("when_blocks", []):
        cond = str(block.get("condition", "")).strip()

        if "==" not in cond and " = " in cond:
            cond = cond.replace(" = ", " == ", 1)

        block["condition"] = cond

        fixed_body = []
        for line in block.get("body", []):
            line = str(line).strip()

            # Token parser may output: say native safe branch selected
            # QVM can read it, but keep it clean and predictable.
            if line.startswith("say ") and '"' not in line:
                msg = line[4:].strip()
                line = f'say "{msg}"'

            fixed_body.append(line)

        block["body"] = fixed_body

    return ast

def run_pipeline(source):
    source = Path(source)

    if not source.exists():
        print("QBIT NOVA file not found: " + str(source))
        return 1

    print("QBIT NOVA v0.9 token pipeline online")
    print("source: " + str(source))
    print("pipeline: UD_SOURCE -> TOKENS -> TOKEN_PARSER_AST -> SEMANTIC -> QBIT_IR -> QVM")

    try:
        ast = token_parser.parse_file(source)
        ast = normalize_ast(ast)
    except SyntaxError as err:
        print("TOKEN_PARSER_RED")
        print(str(err))
        print("QBIT_NOVA_V09_PIPELINE_RED")
        return 1

    print("TOKEN_PARSER_AST_BEGIN")
    print("parser: " + ast.get("parser", "unknown"))
    print("language: " + ast.get("language", ""))
    print("creator: " + ast.get("creator", ""))
    print("team: " + ast.get("team", ""))
    print("brain: " + ast.get("brain", ""))
    print("qbits: " + str(len(ast.get("qbits", []))))
    print("measurements: " + str(len(ast.get("measurements", []))))
    print("when_blocks: " + str(len(ast.get("when_blocks", []))))
    print("adapters: " + str(len(ast.get("adapters", []))))
    print("TOKEN_PARSER_AST_END")

    errors = native.semantic_errors(ast)

    if errors:
        print("SEMANTIC_RED_BEGIN")
        for err in errors:
            print("- " + err)
        print("SEMANTIC_RED_END")
        print("QBIT_NOVA_V09_PIPELINE_RED")
        return 1

    print("SEMANTIC_GREEN")

    print("QBIT_IR_BEGIN")
    for line in native.compile_ir(ast):
        print(line)
    print("QBIT_IR_END")

    print("QVM_RUN_BEGIN")
    for line in native.run_qvm(ast):
        print(line)
    print("QVM_RUN_END")

    print("QBIT_NOVA_V09_PIPELINE_GREEN")
    return 0

def main():
    if len(sys.argv) < 2:
        print("Usage: qbit_nova_v09_pipeline.py <file.ud>")
        return 1

    return run_pipeline(sys.argv[1])

if __name__ == "__main__":
    raise SystemExit(main())
