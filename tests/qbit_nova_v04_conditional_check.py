from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "tools" / "nova_cli.ud"

CASES = [
    {
        "file": ROOT / "examples" / "v2" / "qbit_nova_v04_when_zero.ud",
        "must": [
            "QBIT NOVA source: universal_dragon",
            "Creator: Aslam",
            "Team: Askutty",
            "Brain: NovaKutty",
            "QBIT NOVA v0.4 real conditional online",
            "qbit dragon = |0>",
            "measure dragon => 0",
            "when dragon == 0 selected",
            "safe branch selected",
        ],
        "must_not": [
            "owner approval branch selected",
            "when dragon == 1 selected",
        ],
    },
    {
        "file": ROOT / "examples" / "v2" / "qbit_nova_v04_when_one.ud",
        "must": [
            "QBIT NOVA source: universal_dragon",
            "Creator: Aslam",
            "Team: Askutty",
            "Brain: NovaKutty",
            "QBIT NOVA v0.4 real conditional online",
            "qbit dragon = |1>",
            "measure dragon => 1",
            "when dragon == 1 selected",
            "owner approval branch selected",
        ],
        "must_not": [
            "safe branch selected",
            "when dragon == 0 selected",
        ],
    },
]

def run_case(case):
    result = subprocess.run(
        [sys.executable, str(CLI), "run", str(case["file"])],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
    )

    print("-----", case["file"].name, "-----")
    print(result.stdout)

    if result.stderr:
        print(result.stderr, file=sys.stderr)

    if result.returncode != 0:
        return False

    ok = True

    for item in case["must"]:
        if item not in result.stdout:
            print("MISSING:", item)
            ok = False

    for item in case["must_not"]:
        if item in result.stdout:
            print("UNEXPECTED:", item)
            ok = False

    return ok

def main() -> int:
    good = True

    for case in CASES:
        if not run_case(case):
            good = False

    if not good:
        print("QBIT_NOVA_V04_CONDITIONAL_RED")
        return 1

    print("QBIT_NOVA_V04_CONDITIONAL_GREEN")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
