from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "tools" / "nova_cli.ud"
EXAMPLE = ROOT / "examples" / "v2" / "qbit_nova_v05_ast.ud"

def main() -> int:
    result = subprocess.run(
        [sys.executable, str(CLI), "ast", str(EXAMPLE)],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
    )

    print(result.stdout)

    if result.stderr:
        print(result.stderr, file=sys.stderr)

    if result.returncode != 0:
        return result.returncode

    data = json.loads(result.stdout)

    checks = [
        data.get("language") == "QBIT NOVA",
        data.get("ud") == "Universal Dragon",
        data.get("creator") == "Aslam",
        data.get("team") == "Askutty",
        data.get("brain") == "NovaKutty",
        data.get("nova") == "universal_dragon",
        {"name": "player", "value": "Aslam"} in data.get("memory", []),
        {"name": "mission", "value": "AST proof"} in data.get("memory", []),
        {"name": "dragon", "state": "|0>"} in data.get("qbits", []),
        {"gate": "h", "target": "dragon"} in data.get("gates", []),
        {"target": "dragon"} in data.get("measurements", []),
        "QBIT NOVA v0.5 AST online" in data.get("says", []),
        {"condition": "dragon == 0", "body": ['say "AST safe branch"']} in data.get("when_blocks", []),
        {"condition": "dragon == 1", "body": ['say "AST owner branch"']} in data.get("when_blocks", []),
        {"name": "whatsapp", "body": ["mode safe_reply", "owner_approval required", "dangerous_action deny"]} in data.get("adapters", []),
        "conditional" in data.get("runtime", []),
    ]

    if not all(checks):
        print("QBIT_NOVA_V05_AST_RED")
        return 1

    print("QBIT_NOVA_V05_AST_GREEN")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
