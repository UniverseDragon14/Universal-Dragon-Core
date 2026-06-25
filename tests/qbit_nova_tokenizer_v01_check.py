#!/usr/bin/env python3
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "qbit_nova_tokenizer_v01.py"
SRC = ROOT / "examples" / "v2" / "qbit_nova_dna_v01.qnova"
DOC = ROOT / "docs" / "QBIT_NOVA_TOKENIZER_V0_1.md"

if not TOOL.exists():
    raise SystemExit("MISSING tokenizer tool")

if not SRC.exists():
    raise SystemExit("MISSING DNA qnova source")

if not DOC.exists():
    raise SystemExit("MISSING tokenizer doc")

spec = importlib.util.spec_from_file_location("qbit_nova_tokenizer_v01", TOOL)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

source = SRC.read_text(encoding="utf-8")
tokens = mod.tokenize(source)
pairs = [(t.type, t.value) for t in tokens]

required = [
    ("KEYWORD", "qnova"),
    ("KEYWORD", "identity"),
    ("WORD", "novakutty"),
    ("KEYWORD", "creator"),
    ("WORD", "aslam"),
    ("KEYWORD", "law"),
    ("WORD", "no_existing_language_identity"),
    ("KEYWORD", "qbit"),
    ("KEYWORD", "intent"),
    ("COLON", ":"),
    ("KEYWORD", "rollback"),
    ("KEYWORD", "on_fail"),
    ("KEYWORD", "emit"),
    ("WORD", "QBIT_NOVA_LANGUAGE_DNA_V01"),
    ("EOF", ""),
]

for item in required:
    if item not in pairs:
        raise SystemExit(f"MISSING TOKEN: {item}")

text = DOC.read_text(encoding="utf-8")
for marker in [
    "QBIT NOVA Tokenizer v0.1",
    "Existing host tools are bootstrap tools only",
    "QBIT_NOVA_TOKENIZER_V01",
]:
    if marker not in text:
        raise SystemExit(f"MISSING DOC MARKER: {marker}")

print("QBIT_NOVA_TOKENIZER_V01_GREEN")
