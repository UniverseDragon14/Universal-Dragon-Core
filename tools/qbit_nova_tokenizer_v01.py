#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

KEYWORDS = {
    "qnova",
    "dna",
    "identity",
    "creator",
    "project",
    "team",
    "law",
    "guard",
    "qbit",
    "intent",
    "emit",
    "check",
    "backup",
    "validate",
    "rollback",
    "learn",
    "on_fail",
    "always",
    "first",
    "before_change",
    "after_change",
    "required",
}

SYMBOLS = set("=()[]{}.,+-*/<>")

@dataclass
class Token:
    type: str
    value: str
    line: int
    col: int

    def as_dict(self):
        return {
            "type": self.type,
            "value": self.value,
            "line": self.line,
            "col": self.col,
        }

def is_word_start(ch: str) -> bool:
    return ch.isalpha() or ch == "_"

def is_word_part(ch: str) -> bool:
    return ch.isalnum() or ch in "_-"

def tokenize_line(text: str, line_no: int):
    tokens = []
    i = 0
    n = len(text)

    while i < n:
        ch = text[i]
        col = i + 1

        if ch in " \t":
            i += 1
            continue

        if ch == "#":
            break

        if ch == ":":
            tokens.append(Token("COLON", ":", line_no, col))
            i += 1
            continue

        if ch == '"':
            start = i
            i += 1
            value = ""
            while i < n:
                if text[i] == '"' and text[i - 1] != "\\":
                    break
                value += text[i]
                i += 1
            if i >= n:
                raise SyntaxError(f"Unclosed string at line {line_no}, col {col}")
            i += 1
            tokens.append(Token("STRING", value, line_no, col))
            continue

        if ch == "|" and i + 2 < n and text[i + 2] == ">" and text[i + 1] in "01":
            tokens.append(Token("QSTATE", text[i:i+3], line_no, col))
            i += 3
            continue

        if ch.isdigit():
            start = i
            while i < n and (text[i].isdigit() or text[i] == "."):
                i += 1
            tokens.append(Token("NUMBER", text[start:i], line_no, col))
            continue

        if is_word_start(ch):
            start = i
            while i < n and is_word_part(text[i]):
                i += 1
            value = text[start:i]
            kind = "KEYWORD" if value.lower() in KEYWORDS else "WORD"
            tokens.append(Token(kind, value, line_no, col))
            continue

        if ch in SYMBOLS:
            tokens.append(Token("SYMBOL", ch, line_no, col))
            i += 1
            continue

        raise SyntaxError(f"Unknown character {ch!r} at line {line_no}, col {col}")

    return tokens

def tokenize(source: str):
    tokens = []
    indent_stack = [0]

    for line_no, raw in enumerate(source.splitlines(), start=1):
        if not raw.strip():
            continue

        indent = len(raw) - len(raw.lstrip(" "))
        content = raw[indent:]

        if indent > indent_stack[-1]:
            indent_stack.append(indent)
            tokens.append(Token("INDENT", str(indent), line_no, 1))
        while indent < indent_stack[-1]:
            indent_stack.pop()
            tokens.append(Token("DEDENT", str(indent), line_no, 1))

        tokens.extend(tokenize_line(content, line_no))
        tokens.append(Token("NEWLINE", "\\n", line_no, len(raw) + 1))

    while len(indent_stack) > 1:
        indent_stack.pop()
        tokens.append(Token("DEDENT", "0", line_no if "line_no" in locals() else 1, 1))

    tokens.append(Token("EOF", "", line_no if "line_no" in locals() else 1, 1))
    return tokens

def main(argv):
    if len(argv) != 2:
        print("Usage: qbit_nova_tokenizer_v01.py <file.qnova|file.ud>")
        return 2

    path = Path(argv[1])
    if not path.exists():
        print(f"File not found: {path}")
        return 1

    source = path.read_text(encoding="utf-8")
    tokens = tokenize(source)

    print("QBIT_NOVA_TOKENIZER_V01")
    print(json.dumps([t.as_dict() for t in tokens], indent=2, ensure_ascii=False))
    print("QBIT_NOVA_TOKENIZER_V01_GREEN")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
