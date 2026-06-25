#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import qbit_nova_tokenizer_v01 as tokenizer


class ParserError(Exception):
    pass


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos]

    def at(self, kind, value=None):
        tok = self.peek()
        if tok.type != kind:
            return False
        if value is not None and tok.value != value:
            return False
        return True

    def advance(self):
        tok = self.peek()
        self.pos += 1
        return tok

    def expect(self, kind, value=None):
        tok = self.peek()
        if not self.at(kind, value):
            want = f"{kind}:{value}" if value else kind
            got = f"{tok.type}:{tok.value}"
            raise ParserError(f"Expected {want}, got {got} at line {tok.line}, col {tok.col}")
        return self.advance()

    def skip_newlines(self):
        while self.at("NEWLINE"):
            self.advance()

    def parse(self):
        body = []
        self.skip_newlines()

        while not self.at("EOF"):
            if self.at("DEDENT"):
                self.advance()
                continue
            body.append(self.parse_statement())
            self.skip_newlines()

        return {
            "marker": "QBIT_NOVA_PARSER_V01",
            "type": "Program",
            "body": body,
        }

    def parse_statement(self):
        if self.at("INDENT"):
            self.advance()
            return self.parse_statement()

        head = self.expect_any_word()
        terms = [self.token_node(head)]

        while not self.at("NEWLINE") and not self.at("EOF") and not self.at("DEDENT"):
            if self.at("COLON"):
                self.advance()
                return self.parse_block(terms)

            tok = self.advance()
            terms.append(self.token_node(tok))

        node_type = self.statement_type(terms)
        return {
            "type": node_type,
            "line": head.line,
            "terms": terms,
        }

    def parse_block(self, header_terms):
        line = header_terms[0]["line"]
        self.expect("NEWLINE")
        self.expect("INDENT")

        body = []
        self.skip_newlines()

        while not self.at("DEDENT") and not self.at("EOF"):
            body.append(self.parse_statement())
            self.skip_newlines()

        self.expect("DEDENT")

        return {
            "type": "GuardBlock" if self.term_value(header_terms, 0) == "guard" else "Block",
            "line": line,
            "header": header_terms,
            "body": body,
        }

    def expect_any_word(self):
        tok = self.peek()
        if tok.type not in ("KEYWORD", "WORD"):
            raise ParserError(f"Expected word, got {tok.type}:{tok.value} at line {tok.line}, col {tok.col}")
        return self.advance()

    def token_node(self, tok):
        return {
            "kind": tok.type,
            "value": tok.value,
            "line": tok.line,
            "col": tok.col,
        }

    def term_value(self, terms, index):
        if index >= len(terms):
            return ""
        return str(terms[index].get("value", "")).lower()

    def statement_type(self, terms):
        head = self.term_value(terms, 0)

        if head in ("qnova", "identity", "creator", "project", "team", "dna"):
            return "HeaderStatement"

        if head == "law":
            return "LawStatement"

        if head == "qbit":
            return "QbitStatement"

        if head == "emit":
            return "EmitStatement"

        return "Statement"


def parse_source(source: str):
    tokens = tokenizer.tokenize(source)
    return Parser(tokens).parse()


def main(argv):
    if len(argv) != 2:
        print("Usage: qbit_nova_parser_v01.py <file.qnova|file.ud>")
        return 2

    path = Path(argv[1])
    if not path.exists():
        print(f"File not found: {path}")
        return 1

    ast = parse_source(path.read_text(encoding="utf-8"))

    print("QBIT_NOVA_PARSER_V01")
    print(json.dumps(ast, indent=2, ensure_ascii=False))
    print("QBIT_NOVA_PARSER_V01_GREEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
