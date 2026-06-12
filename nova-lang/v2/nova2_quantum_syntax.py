#!/usr/bin/env python3
import json
import sys
from dataclasses import dataclass
from pathlib import Path

KEYWORDS = {
    "brain",
    "intent",
    "qbit",
    "h",
    "x",
    "z",
    "prob",
    "state",
    "observe",
    "collapse",
    "simulate",
    "guard",
    "when",
    "rollback",
    "say",
}

@dataclass
class Token:
    kind: str
    value: str
    line: int
    col: int

def lex(source: str):
    tokens = []
    i = 0
    line = 1
    col = 1

    def add(kind, value, ln, cl):
        tokens.append(Token(kind, value, ln, cl))

    while i < len(source):
        ch = source[i]

        if ch in " \t\r":
            i += 1
            col += 1
            continue

        if ch == "\n":
            i += 1
            line += 1
            col = 1
            continue

        if ch == "#":
            while i < len(source) and source[i] != "\n":
                i += 1
                col += 1
            continue

        if source.startswith("=>", i):
            add("ARROW", "=>", line, col)
            i += 2
            col += 2
            continue

        if ch in "{}=()":
            add(ch, ch, line, col)
            i += 1
            col += 1
            continue

        if ch == '"':
            ln, cl = line, col
            i += 1
            col += 1
            out = []
            while i < len(source) and source[i] != '"':
                if source[i] == "\n":
                    raise SyntaxError(f"String not closed at line {ln}")
                out.append(source[i])
                i += 1
                col += 1
            if i >= len(source):
                raise SyntaxError(f"String not closed at line {ln}")
            i += 1
            col += 1
            add("STRING", "".join(out), ln, cl)
            continue

        if ch == "|" and i + 2 < len(source) and source[i + 2] == ">":
            value = source[i:i+3]
            if value not in {"|0>", "|1>"}:
                raise SyntaxError(f"Unknown qbit state {value!r} at line {line}")
            add("QSTATE", value, line, col)
            i += 3
            col += 3
            continue

        if ch.isdigit():
            ln, cl = line, col
            out = []
            while i < len(source) and source[i].isdigit():
                out.append(source[i])
                i += 1
                col += 1
            add("NUMBER", "".join(out), ln, cl)
            continue

        if ch.isalpha() or ch == "_":
            ln, cl = line, col
            out = []
            while i < len(source) and (source[i].isalnum() or source[i] == "_"):
                out.append(source[i])
                i += 1
                col += 1
            word = "".join(out)
            add("KEYWORD" if word in KEYWORDS else "ID", word, ln, cl)
            continue

        raise SyntaxError(f"Unexpected character {ch!r} at line {line}, col {col}")

    tokens.append(Token("EOF", "", line, col))
    return tokens

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos]

    def advance(self):
        tok = self.peek()
        self.pos += 1
        return tok

    def expect(self, kind=None, value=None):
        tok = self.peek()
        if kind is not None and tok.kind != kind:
            raise SyntaxError(f"Expected {kind}, got {tok.kind}:{tok.value!r} at line {tok.line}")
        if value is not None and tok.value != value:
            raise SyntaxError(f"Expected {value!r}, got {tok.value!r} at line {tok.line}")
        return self.advance()

    def parse_program(self):
        body = []
        while self.peek().kind != "EOF":
            body.append(self.parse_statement())
        return {
            "type": "NovaQuantumFirstProgram",
            "version": "2.2-syntax",
            "body": body,
        }

    def parse_statement(self):
        tok = self.expect("KEYWORD")
        word = tok.value

        if word == "brain":
            name = self.expect("ID").value
            return {"type": "Brain", "name": name}

        if word == "intent":
            value = self.expect("STRING").value
            return {"type": "Intent", "value": value}

        if word == "qbit":
            name = self.expect("ID").value
            self.expect("=")
            state = self.expect("QSTATE").value
            return {"type": "Qbit", "name": name, "state": state}

        if word in {"h", "x", "z", "prob", "state", "observe", "collapse"}:
            target = self.expect("ID").value
            return {"type": word.upper(), "target": target}

        if word == "simulate":
            target = self.expect("ID").value
            self.expect("{")
            branches = []
            while self.peek().value != "}":
                branches.append(self.parse_when_branch())
            self.expect("}")
            return {"type": "Simulate", "target": target, "branches": branches}

        if word == "guard":
            self.expect("{")
            rules = []
            while self.peek().value != "}":
                rules.append(self.parse_when_rule())
            self.expect("}")
            return {"type": "Guard", "rules": rules}

        if word == "rollback":
            return {"type": "Rollback"}

        if word == "say":
            value = self.expect("STRING").value
            return {"type": "Say", "value": value}

        raise SyntaxError(f"Keyword {word!r} not supported at line {tok.line}")

    def parse_when_branch(self):
        self.expect("KEYWORD", "when")
        case = self.expect("NUMBER").value
        self.expect("ARROW")
        outcome = self.expect("STRING").value
        return {"case": int(case), "outcome": outcome}

    def parse_when_rule(self):
        self.expect("KEYWORD", "when")
        case = self.expect("NUMBER").value
        self.expect("ARROW")

        tok = self.peek()

        if tok.kind == "KEYWORD" and tok.value == "rollback":
            self.advance()
            action = {"type": "Rollback"}
        elif tok.kind == "KEYWORD" and tok.value == "say":
            self.advance()
            action = {"type": "Say", "value": self.expect("STRING").value}
        else:
            raise SyntaxError(f"Expected guard action at line {tok.line}")

        return {"case": int(case), "action": action}

def main():
    if len(sys.argv) != 2:
        print("Usage: nova2_quantum_syntax.py file.nova")
        sys.exit(2)

    path = Path(sys.argv[1])
    source = path.read_text(encoding="utf-8")
    tokens = lex(source)
    ast = Parser(tokens).parse_program()
    print(json.dumps(ast, indent=2))

if __name__ == "__main__":
    main()
