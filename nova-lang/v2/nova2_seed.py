#!/usr/bin/env python3
import json
import re
import sys
from dataclasses import dataclass

KEYWORDS = {
    "brain", "let", "say", "fn", "return", "task", "backup",
    "run", "if", "error", "rollback", "qbit", "h", "x", "z", "state", "prob", "reset", "measure"
}

TOKEN_RE = re.compile(
    r"(?P<QSTATE>\|[01]\>)"
    r"|(?P<STRING>\"[^\"\\]*(?:\\.[^\"\\]*)*\")"
    r"|(?P<NUMBER>\d+(?:\.\d+)?)"
    r"|(?P<ID>[A-Za-z_][A-Za-z0-9_]*)"
    r"|(?P<SYMBOL>[{}()=,+\-*/])"
    r"|(?P<SPACE>[ \t]+)"
    r"|(?P<MISMATCH>.)"
)

@dataclass
class Token:
    kind: str
    value: str
    line: int
    col: int

def lex(source: str):
    tokens = []
    for line_no, raw_line in enumerate(source.splitlines(), start=1):
        line = raw_line.split("#", 1)[0]
        for m in TOKEN_RE.finditer(line):
            kind = m.lastgroup
            value = m.group()
            col = m.start() + 1

            if kind == "SPACE":
                continue

            if kind == "ID" and value in KEYWORDS:
                kind = "KEYWORD"

            if kind == "MISMATCH":
                raise SyntaxError(f"Unexpected character {value!r} at line {line_no}, col {col}")

            tokens.append(Token(kind, value, line_no, col))

        tokens.append(Token("NEWLINE", "\\n", line_no, len(raw_line) + 1))

    tokens.append(Token("EOF", "", line_no if source else 1, 1))
    return tokens

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.i = 0

    def peek(self):
        return self.tokens[self.i]

    def advance(self):
        tok = self.peek()
        self.i += 1
        return tok

    def match(self, value=None, kind=None):
        tok = self.peek()
        if value is not None and tok.value != value:
            return False
        if kind is not None and tok.kind != kind:
            return False
        self.advance()
        return True

    def expect(self, value=None, kind=None):
        tok = self.peek()
        if value is not None and tok.value != value:
            raise SyntaxError(f"Expected {value!r}, got {tok.value!r} at line {tok.line}")
        if kind is not None and tok.kind != kind:
            raise SyntaxError(f"Expected {kind}, got {tok.kind} at line {tok.line}")
        return self.advance()

    def skip_newlines(self):
        while self.match(kind="NEWLINE"):
            pass

    def parse_program(self):
        body = []
        self.skip_newlines()
        while self.peek().kind != "EOF":
            body.append(self.parse_statement())
            self.skip_newlines()
        return {"type": "Program", "body": body}

    def parse_statement(self):
        tok = self.peek()

        if tok.kind != "KEYWORD":
            raise SyntaxError(f"Expected statement keyword, got {tok.value!r} at line {tok.line}")

        word = tok.value

        if word == "brain":
            self.advance()
            name = self.expect(kind="ID").value
            return {"type": "Brain", "name": name}

        if word == "let":
            self.advance()
            name = self.expect(kind="ID").value
            self.expect(value="=")
            return {"type": "Let", "name": name, "value": self.collect_expr()}

        if word == "say":
            self.advance()
            return {"type": "Say", "value": self.collect_expr()}

        if word == "qbit":
            self.advance()
            name = self.expect(kind="ID").value
            self.expect(value="=")
            state = self.expect(kind="QSTATE").value
            return {"type": "Qbit", "name": name, "state": state}

        if word in {"h", "x", "z", "state", "prob", "reset", "measure"}:
            self.advance()
            name = self.expect(kind="ID").value
            return {"type": word.upper(), "target": name}

        if word == "backup":
            self.advance()
            return {"type": "Backup"}

        if word == "rollback":
            self.advance()
            return {"type": "Rollback"}

        if word == "run":
            self.advance()
            return {"type": "Run", "command": self.collect_expr()}

        if word in {"fn", "task", "if", "return"}:
            self.advance()
            return {"type": "SeedBlockOrControl", "keyword": word, "tail": self.collect_expr()}

        raise SyntaxError(f"Unsupported keyword {word!r} at line {tok.line}")

    def collect_expr(self):
        parts = []
        while self.peek().kind not in {"NEWLINE", "EOF"}:
            parts.append(self.advance().value)
        return " ".join(parts)

def main():
    if len(sys.argv) != 2:
        print("Usage: nova2_seed.py file.nova")
        sys.exit(2)

    src_path = sys.argv[1]
    source = open(src_path, "r", encoding="utf-8").read()
    tokens = lex(source)
    ast = Parser(tokens).parse_program()

    print("NOVA v2 lexer/parser seed GREEN")
    print(json.dumps(ast, indent=2))

if __name__ == "__main__":
    main()
