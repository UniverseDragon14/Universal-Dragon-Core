#!/usr/bin/env python3
import math
import random
import sys
from pathlib import Path

# Import lexer/parser seed from same folder
sys.path.insert(0, str(Path(__file__).parent))
from nova2_seed import lex, Parser

class QBit:
    def __init__(self, state="|0>"):
        if state == "|1>":
            self.a = 0+0j
            self.b = 1+0j
        else:
            self.a = 1+0j
            self.b = 0+0j

    def h(self):
        a, b = self.a, self.b
        s = math.sqrt(2)
        self.a = (a + b) / s
        self.b = (a - b) / s

    def measure(self):
        p0 = abs(self.a) ** 2
        if random.random() < p0:
            self.a, self.b = 1+0j, 0+0j
            return "0"
        self.a, self.b = 0+0j, 1+0j
        return "1"

    def state_text(self):
        return f"|0>={self.a:.3f} |1>={self.b:.3f}"

class NovaRuntime:
    def __init__(self):
        self.vars = {}
        self.qbits = {}
        self.brain = None

    def eval_value(self, raw):
        raw = raw.strip()

        if raw.startswith('"') and raw.endswith('"'):
            return raw[1:-1]

        if raw in self.vars:
            return self.vars[raw]

        if raw.isdigit():
            return int(raw)

        try:
            return float(raw)
        except ValueError:
            return raw

    def run(self, ast):
        print("NOVA v2 interpreter seed GREEN")

        for node in ast["body"]:
            t = node["type"]

            if t == "Brain":
                self.brain = node["name"]
                print(f"brain {self.brain} online")

            elif t == "Let":
                value = self.eval_value(node["value"])
                self.vars[node["name"]] = value

            elif t == "Say":
                print(self.eval_value(node["value"]))

            elif t == "Qbit":
                q = QBit(node["state"])
                self.qbits[node["name"]] = q
                print(f"qbit {node['name']} = {node['state']}")
                print(f"{node['name']}: {q.state_text()}")

            elif t == "H":
                name = node["target"]
                q = self.qbits[name]
                q.h()
                print(f"h {name}")
                print(f"{name}: {q.state_text()}")

            elif t == "MEASURE":
                name = node["target"]
                q = self.qbits[name]
                result = q.measure()
                print(f"measure {name} => {result}")
                print(f"{name}: {q.state_text()}")

            elif t == "Backup":
                print("backup requested [seed mode]")

            elif t == "Rollback":
                print("rollback requested [seed mode]")

            elif t == "Run":
                print(f"run requested [seed safe mode]: {node['command']}")

            else:
                print(f"seed skipped: {node}")

def main():
    if len(sys.argv) != 2:
        print("Usage: nova2_run.py file.nova")
        sys.exit(2)

    source_path = sys.argv[1]
    source = open(source_path, "r", encoding="utf-8").read()

    tokens = lex(source)
    ast = Parser(tokens).parse_program()

    runtime = NovaRuntime()
    runtime.run(ast)

if __name__ == "__main__":
    main()
