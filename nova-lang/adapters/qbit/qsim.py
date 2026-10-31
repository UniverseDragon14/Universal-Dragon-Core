#!/data/data/com.termux/files/usr/bin/python
import sys, math, random, cmath

class QBit:
    def __init__(self):
        self.a = 1+0j
        self.b = 0+0j

    def x(self):
        self.a, self.b = self.b, self.a

    def h(self):
        a, b = self.a, self.b
        s = math.sqrt(2)
        self.a = (a + b) / s
        self.b = (a - b) / s

    def z(self):
        self.b = -self.b

    def state(self):
        return f"|0>={self.a:.3f} |1>={self.b:.3f}"

    def measure(self):
        p0 = abs(self.a) ** 2
        r = random.random()
        if r < p0:
            self.a, self.b = 1+0j, 0+0j
            return "0"
        self.a, self.b = 0+0j, 1+0j
        return "1"

def run_file(path):
    qbits = {}

    for raw in open(path, encoding="utf-8"):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue

        parts = line.split()
        cmd = parts[0].lower()

        if cmd == "qbit":
            name = parts[1]
            qbits[name] = QBit()
            print(f"qbit {name} = |0>")

        elif cmd == "x":
            qbits[parts[1]].x()
            print(f"x {parts[1]}")

        elif cmd == "h":
            qbits[parts[1]].h()
            print(f"h {parts[1]}")

        elif cmd == "z":
            qbits[parts[1]].z()
            print(f"z {parts[1]}")

        elif cmd == "state":
            name = parts[1]
            print(f"{name}: {qbits[name].state()}")

        elif cmd == "measure":
            name = parts[1]
            print(f"measure {name} => {qbits[name].measure()}")

        else:
            print(f"unknown qbit command: {line}")

if len(sys.argv) < 2:
    print("Use: novaq file.qnova")
    sys.exit(1)

run_file(sys.argv[1])
