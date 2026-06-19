#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "nova-lang" / "v2" / "nova2_run.py"

TESTS = [
    {
        "name": "intent",
        "file": ROOT / "examples" / "v2" / "intent_v1_test.nova",
        "must": ["intent locked:", "Intent system online"],
    },
    {
        "name": "simulate",
        "file": ROOT / "examples" / "v2" / "simulate_v1_test.nova",
        "must": ["simulate auth_state", "when 0 => Owner matched", "when 1 => Spoof risk", "Simulate block online"],
    },
    {
        "name": "observe",
        "file": ROOT / "examples" / "v2" / "observe_v1_test.nova",
        "must": ["observe auth_state =>", "Observe system online"],
    },
    {
        "name": "guard",
        "file": ROOT / "examples" / "v2" / "guard_v1_test.nova",
        "must": ["guard auth_state", "guard matched auth_state ==", "Guard system online"],
        "either": ["Access allowed", "rollback requested [guard safe mode]"],
    },
]

def run_nova(path: Path) -> str:
    result = subprocess.run(
        [sys.executable, str(RUNNER), str(path)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    out = result.stdout + result.stderr
    if result.returncode != 0:
        print(out)
        raise SystemExit(f"FAIL: {path.name} exited with {result.returncode}")
    return out

print("NOVA Quantum-Intent Core check")
print("Running intent/simulate/observe/guard tests...\n")

for test in TESTS:
    out = run_nova(test["file"])

    for expected in test["must"]:
        if expected not in out:
            print(out)
            raise SystemExit(f"FAIL: {test['name']} missing: {expected}")

    if "either" in test and not any(x in out for x in test["either"]):
        print(out)
        raise SystemExit(f"FAIL: {test['name']} missing one allowed branch")

    print(f"PASS: {test['name']}")

print("\nPASS: NOVA Quantum-Intent Core stable.")
