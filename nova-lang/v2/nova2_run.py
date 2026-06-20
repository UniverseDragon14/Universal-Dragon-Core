#!/usr/bin/env python3
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from nova2_seed import lex, Parser

def cfmt(z):
    return f"{z.real:.3f}{z.imag:+.3f}j"

class QuantumWorld:
    def __init__(self):
        self.names = []
        self.amps = [1+0j]

    def add_qbit(self, name, state="|0>"):
        if name in self.names:
            raise RuntimeError(f"Qbit already exists: {name}")

        old = self.amps
        new = []

        for amp in old:
            if state == "|1>":
                new.extend([0+0j, amp])
            else:
                new.extend([amp, 0+0j])

        self.names.append(name)
        self.amps = new

    def q_index(self, name):
        if name not in self.names:
            raise RuntimeError(f"Unknown qbit: {name}")
        return self.names.index(name)

    def mask(self, name):
        n = len(self.names)
        i = self.q_index(name)
        return 1 << (n - 1 - i)

    def apply_gate(self, name, matrix):
        mask = self.mask(name)
        old = self.amps[:]
        new = old[:]

        a, b = matrix[0]
        c, d = matrix[1]

        for i in range(len(old)):
            if i & mask:
                continue

            j = i | mask
            v0 = old[i]
            v1 = old[j]

            new[i] = a * v0 + b * v1
            new[j] = c * v0 + d * v1

        self.amps = new

    def h(self, name):
        s = math.sqrt(2)
        self.apply_gate(name, [[1/s, 1/s], [1/s, -1/s]])

    def x(self, name):
        self.apply_gate(name, [[0, 1], [1, 0]])

    def z(self, name):
        self.apply_gate(name, [[1, 0], [0, -1]])

    def cnot(self, control, target):
        if control == target:
            raise RuntimeError("CNOT control and target cannot be same")

        cmask = self.mask(control)
        tmask = self.mask(target)
        new = self.amps[:]

        for i in range(len(self.amps)):
            control_is_1 = bool(i & cmask)
            target_is_0 = not bool(i & tmask)

            if control_is_1 and target_is_0:
                j = i | tmask
                new[i], new[j] = new[j], new[i]

        self.amps = new

    def prob(self, name):
        mask = self.mask(name)
        p0 = 0.0
        p1 = 0.0

        for i, amp in enumerate(self.amps):
            if i & mask:
                p1 += abs(amp) ** 2
            else:
                p0 += abs(amp) ** 2

        return p0, p1

    def reset(self, name):
        mask = self.mask(name)
        new = [0+0j for _ in self.amps]

        for i in range(len(self.amps)):
            if i & mask:
                continue

            j = i | mask
            p = abs(self.amps[i]) ** 2 + abs(self.amps[j]) ** 2
            new[i] = math.sqrt(p) + 0j

        self.amps = new

    def measure(self, name):
        mask = self.mask(name)
        p0, p1 = self.prob(name)

        result = "0" if random.random() < p0 else "1"
        keep_bit = 0 if result == "0" else mask

        new = []
        norm = math.sqrt(p0 if result == "0" else p1)

        for i, amp in enumerate(self.amps):
            if (i & mask) == keep_bit and norm > 0:
                new.append(amp / norm)
            else:
                new.append(0+0j)

        self.amps = new
        return result

    def single_state_text(self, name):
        if len(self.names) == 1:
            return f"|0>={cfmt(self.amps[0])} |1>={cfmt(self.amps[1])}"

        p0, p1 = self.prob(name)
        return f"{name}: P(0)={p0:.3f} P(1)={p1:.3f}"

    def prob_text(self, name):
        p0, p1 = self.prob(name)
        return f"P(0)={p0:.3f} P(1)={p1:.3f}"

    def register_text(self):
        n = len(self.names)
        if n == 0:
            return "empty"

        out = []
        for i, amp in enumerate(self.amps):
            if abs(amp) > 1e-9:
                bits = format(i, f"0{n}b")
                out.append(f"|{bits}>={cfmt(amp)}")

        return " ".join(out) if out else "zero"

class NovaRuntime:
    def __init__(self):
        self.vars = {}
        self.qworld = QuantumWorld()
        self.brain = None
        self.intent = None

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
        print("NOVA v2 interpreter CNOT entanglement GREEN")

        for node in ast["body"]:
            t = node["type"]

            if t == "Brain":
                self.brain = node["name"]
                print(f"brain {self.brain} online")

            elif t == "Intent":
                self.intent = self.eval_value(node["value"])
                print(f"intent locked: {self.intent}")

            elif t == "Let":
                self.vars[node["name"]] = self.eval_value(node["value"])

            elif t == "Say":
                print(self.eval_value(node["value"]))

            elif t == "Qbit":
                name = node["name"]
                self.qworld.add_qbit(name, node["state"])
                print(f"qbit {name} = {node['state']}")
                print(f"register: {self.qworld.register_text()}")

            elif t == "Simulate":
                target = node["target"]
                print(f"simulate {target}")
                for case in node["cases"]:
                    result = self.eval_value(case["result"])
                    print(f"when {case['value']} => {result}")

            elif t == "H":
                name = node["target"]
                self.qworld.h(name)
                print(f"h {name}")
                print(f"register: {self.qworld.register_text()}")

            elif t == "X":
                name = node["target"]
                self.qworld.x(name)
                print(f"x {name}")
                print(f"register: {self.qworld.register_text()}")

            elif t == "Z":
                name = node["target"]
                self.qworld.z(name)
                print(f"z {name}")
                print(f"register: {self.qworld.register_text()}")

            elif t == "CNOT":
                control = node["control"]
                target = node["target"]
                self.qworld.cnot(control, target)
                print(f"cnot {control} {target}")
                print(f"register: {self.qworld.register_text()}")

            elif t == "STATE":
                name = node["target"]
                print(f"state {name}")
                print(self.qworld.single_state_text(name))
                print(f"register: {self.qworld.register_text()}")

            elif t == "PROB":
                name = node["target"]
                print(f"prob {name}")
                print(f"{name}: {self.qworld.prob_text(name)}")

            elif t == "RESET":
                name = node["target"]
                self.qworld.reset(name)
                print(f"reset {name}")
                print(f"register: {self.qworld.register_text()}")

            elif t == "Patch":
                rel_path = self.eval_value(node["path"])
                root = Path.cwd().resolve()
                target = (root / rel_path).resolve()

                if not str(target).startswith(str(root)):
                    print(f"patch blocked outside project: {rel_path}")
                    continue

                if not target.exists():
                    print(f"patch file not found: {rel_path}")
                    continue

                text = target.read_text()
                changed = False

                for op in node["operations"]:
                    if op["op"] == "replace":
                        old = self.eval_value(op["old"])
                        new = self.eval_value(op["new"])

                        if old not in text:
                            print(f"patch replace skipped: text not found in {rel_path}")
                        else:
                            text = text.replace(old, new)
                            changed = True
                            print(f"patch replace applied: {rel_path}")

                if changed:
                    target.write_text(text)
                    print(f"patch saved: {rel_path}")
                else:
                    print(f"patch no changes: {rel_path}")

            elif t == "OBSERVE":
                name = node["target"]
                result = self.qworld.measure(name)
                self.vars[name] = result
                self.vars[f"{name}_observed"] = result
                print(f"observe {name} => {result}")
                print(f"register: {self.qworld.register_text()}")

            elif t == "Guard":
                target = node["target"]
                observed = self.vars.get(target, self.vars.get(f"{target}_observed"))

                print(f"guard {target}")

                if observed is None:
                    print(f"guard {target}: no observed value")
                    continue

                matched = False

                for case in node["cases"]:
                    if str(case["value"]) == str(observed):
                        matched = True
                        action = case["action"]
                        print(f"guard matched {target} == {observed}")

                        if action == "rollback":
                            print("rollback requested [guard safe mode]")
                        elif action == "say":
                            print(self.eval_value(case["message"]))
                        else:
                            print(f"guard action: {action}")

                if not matched:
                    print(f"guard {target}: no matching case for {observed}")

            elif t == "MEASURE":
                name = node["target"]
                result = self.qworld.measure(name)
                print(f"measure {name} => {result}")
                print(f"register: {self.qworld.register_text()}")

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
