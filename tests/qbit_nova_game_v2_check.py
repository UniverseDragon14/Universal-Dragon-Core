from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "tools" / "nova_cli.ud"

CASES = [
    {
        "file": ROOT / "examples" / "v2" / "qbit_nova_game_v2_safe_path.ud",
        "must": [
            "QBIT NOVA Game v2: Dragon Choice",
            "memory player = Aslam",
            "memory mission = unlock dragon gate",
            "measure dragon => 0",
            "when dragon == 0 selected",
            "GAME PATH: safe route unlocked",
            "RESULT: dragon gate opened",
        ],
        "must_not": [
            "GAME PATH: boss approval route",
            "owner approval needed",
            "when dragon == 1 selected",
        ],
    },
    {
        "file": ROOT / "examples" / "v2" / "qbit_nova_game_v2_boss_path.ud",
        "must": [
            "QBIT NOVA Game v2: Dragon Choice",
            "memory player = Aslam",
            "memory mission = face boss gate",
            "measure dragon => 1",
            "when dragon == 1 selected",
            "GAME PATH: boss approval route",
            "RESULT: owner approval needed",
        ],
        "must_not": [
            "GAME PATH: safe route unlocked",
            "dragon gate opened",
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
        print("QBIT_NOVA_GAME_V2_RED")
        return 1

    print("QBIT_NOVA_GAME_V2_GREEN")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
