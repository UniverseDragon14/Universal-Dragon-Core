#!/usr/bin/env python3
import json
import sys
from pathlib import Path

LANGUAGE = "QBIT NOVA"
VERSION = "v0.8-tokenizer"

KEYWORDS = {
    "nova",
    "creator",
    "team",
    "brain",
    "memory",
    "say",
    "qbit",
    "measure",
    "when",
    "adapter",
    "runtime",
    "mode",
    "owner_approval",
    "risky_action",
    "required",
    "deny",
    "safe_reply",
}

SYMBOLS = {
    "=": "EQUAL",
    ":": "COLON",
    "(": "LPAREN",
    ")": "RPAREN",
    ",": "COMMA",
}

def token(kind, value, line, col):
    return {
        "type": kind,
        "value": value,
        "line": line,
        "col": col,
    }

def strip_comment(line):
    in_string = False
    quote = ""
    out = []

    for ch in line:
        if ch in ['"', "'"]:
            if not in_string:
                in_string = True
                quote = ch
            elif quote == ch:
                in_string = False
                quote = ""
            out.append(ch)
            continue

        if ch == "#" and not in_string:
            break

        out.append(ch)

    return "".join(out)

def read_string(line, i, line_no):
    quote = line[i]
    start = i
    i += 1
    value = []

    while i < len(line):
        ch = line[i]

        if ch == "\\" and i + 1 < len(line):
            value.append(line[i + 1])
            i += 2
            continue

        if ch == quote:
            return "".join(value), i + 1, start + 1

        value.append(ch)
        i += 1

    raise SyntaxError(f"Unclosed string at line {line_no}")

def read_word(line, i):
    start = i
    while i < len(line):
        ch = line[i]
        if ch.isalnum() or ch in ["_", "-", "."]:
            i += 1
        else:
            break
    return line[start:i], i, start + 1

def read_qstate(line, i, line_no):
    start = i
    i += 1
    value = ["|"]

    while i < len(line):
        ch = line[i]
        value.append(ch)

        if ch == ">":
            return "".join(value), i + 1, start + 1

        i += 1

    raise SyntaxError(f"Unclosed qbit state at line {line_no}")

def tokenize_text(text):
    tokens = []
    indent_stack = [0]

    lines = text.splitlines()

    for line_no, original in enumerate(lines, 1):
        raw = strip_comment(original.rstrip("\n"))
        if not raw.strip():
            continue

        indent = len(raw) - len(raw.lstrip(" "))

        if indent > indent_stack[-1]:
            indent_stack.append(indent)
            tokens.append(token("INDENT", str(indent), line_no, 1))

        while indent < indent_stack[-1]:
            indent_stack.pop()
            tokens.append(token("DEDENT", str(indent_stack[-1]), line_no, 1))

        line = raw.lstrip(" ")
        base_col = indent + 1
        i = 0

        while i < len(line):
            ch = line[i]
            col = base_col + i

            if ch.isspace():
                i += 1
                continue

            if ch in ['"', "'"]:
                value, i, start_col = read_string(line, i, line_no)
                tokens.append(token("STRING", value, line_no, base_col + start_col - 1))
                continue

            if ch == "|":
                value, i, start_col = read_qstate(line, i, line_no)
                tokens.append(token("QSTATE", value, line_no, base_col + start_col - 1))
                continue

            if ch in SYMBOLS:
                tokens.append(token(SYMBOLS[ch], ch, line_no, col))
                i += 1
                continue

            if ch.isdigit():
                start = i
                while i < len(line) and line[i].isdigit():
                    i += 1
                tokens.append(token("NUMBER", line[start:i], line_no, base_col + start))
                continue

            if ch.isalpha() or ch == "_":
                value, i, start_col = read_word(line, i)
                kind = "KEYWORD" if value.lower() in KEYWORDS else "IDENT"
                tokens.append(token(kind, value, line_no, base_col + start_col - 1))
                continue

            if ch == ">":
                tokens.append(token("GT", ch, line_no, col))
                i += 1
                continue

            raise SyntaxError(f"Unexpected character {ch!r} at line {line_no}, col {col}")

        tokens.append(token("NEWLINE", "\\n", line_no, len(original) + 1))

    while len(indent_stack) > 1:
        indent_stack.pop()
        tokens.append(token("DEDENT", str(indent_stack[-1]), len(lines), 1))

    tokens.append(token("EOF", "", len(lines) + 1, 1))
    return tokens

def tokenize_file(path):
    return tokenize_text(Path(path).read_text(encoding="utf-8"))

def main():
    if len(sys.argv) < 2:
        print("Usage: qbit_nova_v08_tokenizer.py <file.ud>")
        return 1

    source = Path(sys.argv[1])

    if not source.exists():
        print("QBIT NOVA file not found: " + str(source))
        return 1

    try:
        tokens = tokenize_file(source)
    except SyntaxError as err:
        print("QBIT NOVA tokenizer RED")
        print(str(err))
        print("QBIT_NOVA_V08_TOKENIZER_RED")
        return 1

    print("QBIT NOVA v0.8 tokenizer online")
    print("source: " + str(source))
    print("tokens: " + str(len(tokens)))
    print(json.dumps(tokens, indent=2))
    print("QBIT_NOVA_V08_TOKENIZER_GREEN")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
