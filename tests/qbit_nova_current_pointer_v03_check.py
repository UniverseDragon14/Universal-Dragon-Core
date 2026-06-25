from pathlib import Path

p = Path("docs/QBIT_NOVA_CURRENT_POINTER_V0_3.md")

if not p.exists():
    raise SystemExit("MISSING CURRENT POINTER V0.3")

text = p.read_text(encoding="utf-8")

checks = [
    "QBIT_NOVA_CURRENT_POINTER_V03",
    "QBIT NOVA language/core only",
    "qbit-nova-v1.4.0-dev-qbc-file-writer-v03-fix1-green",
    "QBC File Writer v0.3 fix1 GREEN",
    "real .qbc file",
    "QBIT NOVA QBC File Loader / Reader v0.3",
    "~/qbit-nova-labs/Universal-Dragon-Core-v02",
    "~/ud-github-sync",
]

for c in checks:
    if c not in text:
        raise SystemExit(f"MISSING MARKER: {c}")

print("QBIT_NOVA_CURRENT_POINTER_V03_GREEN")
