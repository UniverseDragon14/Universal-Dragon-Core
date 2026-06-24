from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "tools" / "nova_cli.ud"
WORLD = ROOT / "examples" / "v2" / "qbit_nova_world.ud"

REQUIRED = [
    "QBIT NOVA source: universal_dragon",
    "Creator: Aslam",
    "Team: Askutty",
    "Brain: NovaKutty",
    "QBIT NOVA language online",
    "qbit dragon = |0>",
    "h dragon",
    "measure dragon =>",
    "screen main block loaded",
    "Title: Universal Dragon",
    "guard block loaded",
    "owner_approval required",
    "dangerous_action deny",
]

def main() -> int:
    if not CLI.exists():
        print(f"Missing CLI: {CLI}")
        return 1

    if not WORLD.exists():
        print(f"Missing world file: {WORLD}")
        return 1

    result = subprocess.run(
        [sys.executable, str(CLI), "run", str(WORLD)],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
    )

    print(result.stdout)

    if result.stderr:
        print(result.stderr, file=sys.stderr)

    if result.returncode != 0:
        print(f"QBIT NOVA run failed: {result.returncode}")
        return result.returncode

    missing = [item for item in REQUIRED if item not in result.stdout]

    if missing:
        print("QBIT NOVA contract missing:")
        for item in missing:
            print(f"- {item}")
        return 1

    print("QBIT_NOVA_UD_CONTRACT_GREEN")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
