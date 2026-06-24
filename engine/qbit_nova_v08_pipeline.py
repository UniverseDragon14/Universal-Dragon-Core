#!/usr/bin/env python3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE_DIR = ROOT / "engine"

sys.path.insert(0, str(ENGINE_DIR))

import qbit_nova_v08_tokenizer as tokenizer
import qbit_nova_v07_engine as native

def run_pipeline(source):
    source = Path(source)

    if not source.exists():
        print("QBIT NOVA file not found: " + str(source))
        return 1

    print("QBIT NOVA v0.8 pipeline online")
    print("source: " + str(source))
    print("pipeline: UD_SOURCE -> TOKENS -> AST -> QBIT_IR -> QVM")

    try:
        tokens = tokenizer.tokenize_file(source)
    except SyntaxError as err:
        print("TOKENIZER RED")
        print(str(err))
        print("QBIT_NOVA_V08_PIPELINE_RED")
        return 1

    print("TOKENS_BEGIN")
    print("token_count: " + str(len(tokens)))
    print("first_token: " + tokens[0]["type"] + ":" + tokens[0]["value"])
    print("last_token: " + tokens[-1]["type"])
    print("TOKENS_END")

    ast = native.parse_ud(source)
    errors = native.semantic_errors(ast)

    print("AST_BEGIN")
    print("language: " + ast.get("language", ""))
    print("creator: " + ast.get("creator", ""))
    print("team: " + ast.get("team", ""))
    print("brain: " + ast.get("brain", ""))
    print("qbits: " + str(len(ast.get("qbits", []))))
    print("measurements: " + str(len(ast.get("measurements", []))))
    print("when_blocks: " + str(len(ast.get("when_blocks", []))))
    print("adapters: " + str(len(ast.get("adapters", []))))
    print("AST_END")

    if errors:
        print("SEMANTIC_RED_BEGIN")
        for err in errors:
            print("- " + err)
        print("SEMANTIC_RED_END")
        print("QBIT_NOVA_V08_PIPELINE_RED")
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

    print("QBIT_NOVA_V08_PIPELINE_GREEN")
    return 0

def main():
    if len(sys.argv) < 2:
        print("Usage: qbit_nova_v08_pipeline.py <file.ud>")
        return 1

    return run_pipeline(sys.argv[1])

if __name__ == "__main__":
    raise SystemExit(main())
