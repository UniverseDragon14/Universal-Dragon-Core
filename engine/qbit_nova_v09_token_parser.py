#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE_DIR = ROOT / "engine"
sys.path.insert(0, str(ENGINE_DIR))

import qbit_nova_v08_tokenizer as tokenizer

LANGUAGE = "QBIT NOVA"
UD = "Universal Dragon"
CREATOR = "Aslam"
TEAM = "Askutty"
BRAIN = "NovaKutty"
VERSION = "v0.9-token-parser"

def proper_identity(kind, value):
    value = str(value or "").strip()
    table = {
        "creator": ("aslam", "Aslam"),
        "team": ("askutty", "Askutty"),
        "brain": ("novakutty", "NovaKutty"),
    }
    low, proper = table.get(kind, ("", value))
    return proper if value.lower() == low else value

class TokenParser:
    def __init__(self, tokens, source=""):
        self.tokens = tokens
        self.i = 0
        self.source = source

    def current(self):
        if self.i >= len(self.tokens):
            return {"type": "EOF", "value": "", "line": -1, "col": -1}
        return self.tokens[self.i]

    def peek(self, offset=1):
        j = self.i + offset
        if j >= len(self.tokens):
            return {"type": "EOF", "value": "", "line": -1, "col": -1}
        return self.tokens[j]

    def advance(self):
        tok = self.current()
        self.i += 1
        return tok

    def match_value(self, value):
        return str(self.current().get("value", "")).lower() == value.lower()

    def match_type(self, kind):
        return self.current().get("type") == kind

    def skip_newlines(self):
        while self.match_type("NEWLINE"):
            self.advance()

    def expect_value(self, value):
        tok = self.current()
        if str(tok.get("value", "")).lower() != value.lower():
            raise SyntaxError(f"Expected {value}, got {tok.get('value')} at line {tok.get('line')}")
        return self.advance()

    def expect_type(self, kind):
        tok = self.current()
        if tok.get("type") != kind:
            raise SyntaxError(f"Expected {kind}, got {tok.get('type')} at line {tok.get('line')}")
        return self.advance()

    def line_values_until_newline(self):
        values = []
        while not self.match_type("NEWLINE") and not self.match_type("EOF"):
            values.append(str(self.advance().get("value", "")))
        if self.match_type("NEWLINE"):
            self.advance()
        return " ".join([v for v in values if v]).strip()

    def parse(self):
        ast = {
            "language": LANGUAGE,
            "version": VERSION,
            "ud": UD,
            "source": self.source,
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
            "parser": "token_stream",
        }

        while not self.match_type("EOF"):
            self.skip_newlines()

            if self.match_type("EOF"):
                break

            if self.match_type("DEDENT"):
                self.advance()
                continue

            if self.match_type("INDENT"):
                self.advance()
                continue

            if self.match_value("nova"):
                self.advance()
                ast["nova"] = self.line_values_until_newline()
                continue

            if self.match_value("creator"):
                self.advance()
                ast["creator"] = proper_identity("creator", self.line_values_until_newline())
                continue

            if self.match_value("team"):
                self.advance()
                ast["team"] = proper_identity("team", self.line_values_until_newline())
                continue

            if self.match_value("brain"):
                self.advance()
                ast["brain"] = proper_identity("brain", self.line_values_until_newline())
                continue

            if self.match_value("memory"):
                self.advance()
                name = self.expect_type("IDENT").get("value")
                self.expect_type("EQUAL")
                value = self.line_values_until_newline()
                ast["memory"].append({"name": name, "value": value})
                continue

            if self.match_value("say"):
                self.advance()
                ast["says"].append(self.line_values_until_newline())
                continue

            if self.match_value("qbit"):
                self.advance()
                name = self.expect_type("IDENT").get("value")
                self.expect_type("EQUAL")
                state = self.expect_type("QSTATE").get("value")
                ast["qbits"].append({"name": name, "state": state})
                self.line_values_until_newline()
                continue

            if self.match_value("measure"):
                self.advance()
                target = self.line_values_until_newline()
                ast["measurements"].append({"target": target})
                continue

            if self.match_value("runtime"):
                self.advance()
                ast["runtime"].append(self.line_values_until_newline())
                continue

            if self.match_value("when"):
                ast["when_blocks"].append(self.parse_when_block())
                continue

            if self.match_value("adapter"):
                ast["adapters"].append(self.parse_adapter_block())
                continue

            raise SyntaxError(
                "Unexpected token "
                + str(self.current().get("value"))
                + " at line "
                + str(self.current().get("line"))
            )

        return ast

    def parse_when_block(self):
        self.expect_value("when")
        qbit_name = self.expect_type("IDENT").get("value")

        self.expect_type("EQUAL")
        self.expect_type("EQUAL")

        number = self.expect_type("NUMBER").get("value")
        condition = f"{qbit_name} == {number}"

        self.expect_type("COLON")
        if self.match_type("NEWLINE"):
            self.advance()

        body = []
        if self.match_type("INDENT"):
            self.advance()

            while not self.match_type("DEDENT") and not self.match_type("EOF"):
                if self.match_type("NEWLINE"):
                    self.advance()
                    continue
                body.append(self.line_values_until_newline())

            if self.match_type("DEDENT"):
                self.advance()

        return {
            "condition": condition,
            "body": body,
        }

    def parse_adapter_block(self):
        self.expect_value("adapter")
        name = self.line_values_until_colon()

        self.expect_type("COLON")
        if self.match_type("NEWLINE"):
            self.advance()

        body = []
        if self.match_type("INDENT"):
            self.advance()

            while not self.match_type("DEDENT") and not self.match_type("EOF"):
                if self.match_type("NEWLINE"):
                    self.advance()
                    continue
                body.append(self.line_values_until_newline())

            if self.match_type("DEDENT"):
                self.advance()

        return {
            "name": name,
            "body": body,
        }

    def line_values_until_colon(self):
        values = []
        while not self.match_type("COLON") and not self.match_type("EOF"):
            values.append(str(self.advance().get("value", "")))
        return " ".join([v for v in values if v]).strip()

def parse_file(path):
    source = Path(path)
    tokens = tokenizer.tokenize_file(source)
    parser = TokenParser(tokens, source=str(source))
    return parser.parse()

def main():
    if len(sys.argv) < 2:
        print("Usage: qbit_nova_v09_token_parser.py <file.ud>")
        return 1

    source = Path(sys.argv[1])

    if not source.exists():
        print("QBIT NOVA file not found: " + str(source))
        return 1

    try:
        ast = parse_file(source)
    except SyntaxError as err:
        print("QBIT NOVA v0.9 token parser RED")
        print(str(err))
        print("QBIT_NOVA_V09_TOKEN_PARSER_RED")
        return 1

    print("QBIT NOVA v0.9 token parser online")
    print("source: " + str(source))
    print(json.dumps(ast, indent=2))
    print("QBIT_NOVA_V09_TOKEN_PARSER_GREEN")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
