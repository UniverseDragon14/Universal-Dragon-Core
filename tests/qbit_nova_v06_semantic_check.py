from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "tools" / "nova_cli.ud"
GOOD = ROOT / "examples" / "v2" / "qbit_nova_v06_semantic_good.ud"
BAD = ROOT / "examples" / "v2" / "qbit_nova_v06_semantic_bad.ud"

def run_case(path: Path):
    return subprocess.run(
        [sys.executable, str(CLI), "check", str(path)],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
    )

def main() -> int:
    good = run_case(GOOD)
    print("----- GOOD -----")
    print(good.stdout)
    if good.stderr:
        print(good.stderr, file=sys.stderr)

    if good.returncode != 0 or "QBIT_NOVA_V06_SEMANTIC_GREEN" not in good.stdout:
        print("QBIT_NOVA_V06_GOOD_CASE_RED")
        return 1

    bad = run_case(BAD)
    print("----- BAD -----")
    print(bad.stdout)
    if bad.stderr:
        print(bad.stderr, file=sys.stderr)

    if bad.returncode == 0 or "QBIT_NOVA_V06_SEMANTIC_RED" not in bad.stdout:
        print("QBIT_NOVA_V06_BAD_CASE_RED")
        return 1

    required_bad_markers = [
        "creator must be Aslam",
        "qbit dragon has invalid state |9>",
        "when qbit dragon must be measured before branch",
        "adapter whatsapp missing: mode safe_reply",
        "adapter whatsapp missing: owner_approval required",
        "adapter whatsapp missing: dangerous_action deny",
    ]

    for marker in required_bad_markers:
        if marker not in bad.stdout:
            print("MISSING BAD MARKER:", marker)
            return 1

    print("QBIT_NOVA_V06_SEMANTIC_CONTRACT_GREEN")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
