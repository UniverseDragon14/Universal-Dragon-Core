from pathlib import Path

p = Path("docs/QBIT_NOVA_CURRENT_POINTER_V0_3_1.md")

if not p.exists():
    raise SystemExit("MISSING CURRENT POINTER V0.3.1")

text = p.read_text(encoding="utf-8")

checks = [
    "QBIT_NOVA_CURRENT_POINTER_V031",
    "QBIT NOVA language/core only",
    "qbit-nova-v1.4.0-dev-current-pointer-v03-green",
    "qbit-nova-v1.4.0-dev-qbc-file-writer-v03-fix1-green",
    "qbit-nova-v1.4.0-dev-qbc-file-loader-v03-green",
    "QBIT NOVA v0.3 bytecode loop is GREEN",
    "Reject unknown FF opcode",
    "QBIT NOVA QBC File Runner v0.3",
    "source.qnova",
    "write output.qbc",
    "load output.qbc",
    "decode safe trace",
    "~/qbit-nova-labs/Universal-Dragon-Core-v02",
    "~/ud-github-sync",
]

for c in checks:
    if c not in text:
        raise SystemExit(f"MISSING MARKER: {c}")

print("QBIT_NOVA_CURRENT_POINTER_V031_GREEN")
