from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "nova-lang" / "v2" / "nova2_run.py"

TESTS = [
    {
        "name": "whatsapp_adapter_contract_v3",
        "file": ROOT / "examples" / "v2" / "whatsapp_adapter_contract_v3.nova",
        "must": [
            "NODE_CHANNEL:WHATSAPP",
            "NODE_ACTION:CALL_SAFE_REPLY",
            "NODE_APPROVAL:NO",
            "NODE_RISK:LOW",
            "NODE_RUNTIME:TEXT_OR_VOICE_NOTE_ONLY",
            "NODE_ALLOWED:YES",
            "NODE_REASON:Safe reply can be sent without live call answering",
        ],
    },
    {
        "name": "universal_adapter_contract_v1",
        "file": ROOT / "examples" / "v2" / "universal_adapter_contract_v1.nova",
        "must": [
            "NODE_CONTRACT:UNIVERSAL_ADAPTER",
            "NODE_CHANNEL:ANY_SAFE_ADAPTER",
            "NODE_ACTION:SAFE_EXECUTION_ALLOWED",
            "NODE_APPROVAL:NO",
            "NODE_RISK:LOW",
            "NODE_RUNTIME:TEXT_UI_API_ONLY",
            "NODE_ALLOWED:YES",
            "NODE_REASON:NOVA permits only safe adapter execution",
        ],
    },
]

def run_contract(test):
    result = subprocess.run(
        ["python3", str(RUNNER), str(test["file"])],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=20,
    )

    output = (result.stdout or "") + (result.stderr or "")

    if result.returncode != 0:
        print(f"FAIL: {test['name']} returned {result.returncode}")
        print(output)
        return False

    missing = [x for x in test["must"] if x not in output]
    if missing:
        print(f"FAIL: {test['name']} missing expected output:")
        for item in missing:
            print(f"  - {item}")
        print("\nOUTPUT:")
        print(output)
        return False

    print(f"PASS: {test['name']}")
    return True

def main():
    ok = True

    if not RUNNER.exists():
        print(f"FAIL: runner not found: {RUNNER}")
        return 1

    for test in TESTS:
        if not test["file"].exists():
            print(f"FAIL: test file not found: {test['file']}")
            ok = False
            continue
        ok = run_contract(test) and ok

    if ok:
        print("PASS: NOVA/QBIT adapter contract tests stable.")
        return 0

    return 1

if __name__ == "__main__":
    sys.exit(main())
