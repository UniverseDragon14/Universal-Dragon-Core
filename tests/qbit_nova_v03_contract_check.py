from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "tools" / "nova_cli.ud"
EXAMPLE = ROOT / "examples" / "v2" / "qbit_nova_v03_adapter.ud"

REQUIRED = [
    "QBIT NOVA source: universal_dragon",
    "Creator: Aslam",
    "Team: Askutty",
    "Brain: NovaKutty",
    "QBIT NOVA v0.3 parser online",
    "memory mission = world record proof",
    "qbit dragon = |0>",
    "h dragon",
    "measure dragon =>",
    "when dragon == 0 block loaded",
    "safe branch",
    "when dragon == 1 block loaded",
    "owner approval branch",
    "adapter whatsapp block loaded",
    "mode safe_reply",
    "owner_approval required",
    "dangerous_action deny",
]

def main() -> int:
    result = subprocess.run(
        [sys.executable, str(CLI), "run", str(EXAMPLE)],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
    )

    print(result.stdout)

    if result.stderr:
        print(result.stderr, file=sys.stderr)

    if result.returncode != 0:
        print(f"QBIT NOVA v0.3 run failed: {result.returncode}")
        return result.returncode

    missing = [item for item in REQUIRED if item not in result.stdout]

    if missing:
        print("QBIT NOVA v0.3 contract missing:")
        for item in missing:
            print(f"- {item}")
        return 1

    print("QBIT_NOVA_V03_CONTRACT_GREEN")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
