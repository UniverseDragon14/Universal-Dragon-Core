#!/usr/bin/env python3
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from nova2_seed import lex, Parser

class QBit:
    def __init__(self, state="|0>"):
        self.set_state(state)

    def set_state(self, state):
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

    def x(self):
        self.a, self.b = self.b, self.a

    def z(self):
        self.b = -self.b

    def reset(self):
        self.a = 1+0j
        self.b = 0+0j

    def prob(self):
        return abs(self.a) ** 2, abs(self.b) ** 2

    def measure(self):
        p0, _ = self.prob()
        if random.random() < p0:
            self.reset()
            return "0"
        self.a = 0+0j
        self.b = 1+0j
        return "1"

    def state_text(self):
        return f"|0>={self.a:.3f} |1>={self.b:.3f}"

    def prob_text(self):
        p0, p1 = self.prob()
        return f"P(0)={p0:.3f} P(1)={p1:.3f}"

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

    def get_qbit(self, name):
        if name not in self.qbits:
            raise RuntimeError(f"Unknown qbit: {name}")
        return self.qbits[name]

    def run(self, ast):
        print("NOVA v2 interpreter QBIT gates GREEN")

        for node in ast["body"]:
            t = node["type"]

            if t == "Brain":
                self.brain = node["name"]
                print(f"brain {self.brain} online")

            elif t == "Let":
                self.vars[node["name"]] = self.eval_value(node["value"])

            elif t == "Say":
                print(self.eval_value(node["value"]))

            elif t == "Qbit":
                q = QBit(node["state"])
                self.qbits[node["name"]] = q
                print(f"qbit {node['name']} = {node['state']}")
                print(f"{node['name']}: {q.state_text()}")

            elif t in {"H", "X", "Z", "STATE", "PROB", "RESET", "MEASURE"}:
                name = node["target"]
                q = self.get_qbit(name)

                if t == "H":
                    q.h()
                    print(f"h {name}")
                    print(f"{name}: {q.state_text()}")

                elif t == "X":
                    q.x()
                    print(f"x {name}")
                    print(f"{name}: {q.state_text()}")

                elif t == "Z":
                    q.z()
                    print(f"z {name}")
                    print(f"{name}: {q.state_text()}")

                elif t == "STATE":
                    print(f"state {name}")
                    print(f"{name}: {q.state_text()}")

                elif t == "PROB":
                    print(f"prob {name}")
                    print(f"{name}: {q.prob_text()}")

                elif t == "RESET":
                    q.reset()
                    print(f"reset {name}")
                    print(f"{name}: {q.state_text()}")

                elif t == "MEASURE":
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

    source = open(sys.argv[1], "r", encoding="utf-8").read()
    tokens = lex(source)
    ast = Parser(tokens).parse_program()
    NovaRuntime().run(ast)

if __name__ == "__main__":
    main()
