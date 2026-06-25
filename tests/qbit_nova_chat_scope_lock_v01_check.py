from pathlib import Path

p = Path("docs/QBIT_NOVA_CHAT_SCOPE_LOCK_V0_1.md")

if not p.exists():
    raise SystemExit("MISSING CHAT SCOPE LOCK")

text = p.read_text(encoding="utf-8")

checks = [
    "QBIT_NOVA_CHAT_SCOPE_LOCK_V01",
    "QBIT NOVA language/core only",
    "Do not mix other app missions into this chat",
    "~/qbit-nova-labs/Universal-Dragon-Core-v02",
    "~/ud-github-sync",
    "self-hosting roadmap",
]

for c in checks:
    if c not in text:
        raise SystemExit(f"MISSING MARKER: {c}")

print("QBIT_NOVA_CHAT_SCOPE_LOCK_V01_GREEN")
