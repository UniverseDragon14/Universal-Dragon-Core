#!/usr/bin/env python3
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "nova-lang" / "v2" / "nova2_run.py"
TEST_FILE = ROOT / "examples" / "v2" / "qbit_bell_cnot_test.nova"

counts = {
    "00": 0,
    "01": 0,
    "10": 0,
    "11": 0,
}

bad_pairs = []

print("NOVA QBIT Bell repeat check")
print("Running Bell/CNOT test 20 times...")
print()

for i in range(1, 21):
    result = subprocess.run(
        [sys.executable, str(RUNNER), str(TEST_FILE)],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print("Runtime failed")
        print(result.stderr)
        sys.exit(1)

    out = result.stdout

    ma = re.search(r"measure a => ([01])", out)
    mb = re.search(r"measure b => ([01])", out)

    if not ma or not mb:
        print("Could not read measurement output")
        print(out)
        sys.exit(1)

    pair = ma.group(1) + mb.group(1)
    counts[pair] += 1

    print(f"Run {i:02d}: {pair}")

    if pair in {"01", "10"}:
        bad_pairs.append(pair)

print()
print("Counts:")
for pair, count in counts.items():
    print(f"{pair}: {count}")

print()

if bad_pairs:
    print("FAIL: Bell linked measurement broke.")
    print("Bad pairs:", bad_pairs)
    sys.exit(1)

print("PASS: Bell linked measurement stable.")
print("Only 00 and 11 appeared. 01 and 10 did not appear.")
