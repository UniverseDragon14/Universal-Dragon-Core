#!/usr/bin/env python3
"""
Universal Dragon / NOVA Project Analyzer

Safe architecture review tool for Universal Dragon project folders.
Supports:
- Groq OpenAI-compatible API with openai/gpt-oss-120b
- OpenAI API as optional fallback

Recommended Groq usage:
  export AI_PROVIDER="groq"
  export GROQ_API_KEY="your_groq_api_key_here"
  export GROQ_MODEL="openai/gpt-oss-120b"
  python tools/analyze_universal_dragon.py /path/to/project

Optional OpenAI usage:
  export AI_PROVIDER="openai"
  export OPENAI_API_KEY="your_openai_api_key_here"
  export OPENAI_MODEL="gpt-5.5"
  python tools/analyze_universal_dragon.py /path/to/project
"""

from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

try:
    from openai import OpenAI
except ImportError as exc:
    raise SystemExit("OpenAI Python package not installed. Run: pip install openai") from exc


AI_PROVIDER = os.getenv("AI_PROVIDER", "groq").strip().lower()
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.5")
DEFAULT_MODEL = GROQ_MODEL if AI_PROVIDER == "groq" else OPENAI_MODEL
GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")

MAX_TOTAL_CHARS = int(os.getenv("UD_MAX_ANALYSIS_CHARS", "70000"))
MAX_FILE_CHARS = int(os.getenv("UD_MAX_FILE_CHARS", "9000"))

ALLOWED_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".html", ".css", ".json", ".md", ".txt",
    ".yml", ".yaml", ".toml", ".sh", ".service", ".env.example"
}

SKIP_DIRS = {
    ".git", ".venv", "venv", "env", "node_modules", "__pycache__", ".next",
    "dist", "build", "out", "target", ".cache", ".pytest_cache", ".mypy_cache",
    "logs", "log", "backups", "backup", "tmp", "temp"
}

SECRET_NAME_PARTS = {
    ".env", "secret", "secrets", "token", "apikey", "api_key", "password", "passwd",
    "private", "credential", "credentials", "id_rsa", "id_ed25519", ".pem", ".key"
}

SECRET_PATTERNS = [
    (re.compile(r"sk-proj-[A-Za-z0-9_\-]{20,}"), "sk-proj-***REDACTED***"),
    (re.compile(r"sk-[A-Za-z0-9_\-]{20,}"), "sk-***REDACTED***"),
    (re.compile(r"gsk_[A-Za-z0-9_\-]{20,}"), "gsk_***REDACTED***"),
    (re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[^'\"\n\s]+"), r"\1=***REDACTED***"),
]


@dataclass
class FileChunk:
    path: Path
    content: str


def should_skip_path(path: Path, root: Path) -> bool:
    rel_parts = path.relative_to(root).parts
    lowered_parts = [p.lower() for p in rel_parts]

    if any(part in SKIP_DIRS for part in lowered_parts):
        return True

    name = path.name.lower()
    if any(secret in name for secret in SECRET_NAME_PARTS):
        if name == ".env.example" or name.endswith(".env.example"):
            return False
        return True

    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        return True

    return False


def redact_secrets(text: str) -> str:
    redacted = text
    for pattern, replacement in SECRET_PATTERNS:
        redacted = pattern.sub(replacement, redacted)
    return redacted


def read_project_files(root: Path) -> list[FileChunk]:
    chunks: list[FileChunk] = []
    total = 0

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if should_skip_path(path, root):
            continue

        try:
            raw = path.read_text(encoding="utf-8", errors="ignore")
        except Exception as exc:
            raw = f"[READ_ERROR] {exc}"

        raw = redact_secrets(raw)
        if len(raw) > MAX_FILE_CHARS:
            raw = raw[:MAX_FILE_CHARS] + "\n\n[TRUNCATED: file too large]\n"

        chunks.append(FileChunk(path=path.relative_to(root), content=raw))
        total += len(raw)

        if total >= MAX_TOTAL_CHARS:
            break

    return chunks


def build_prompt(root: Path, chunks: Iterable[FileChunk]) -> str:
    files_text = []
    for chunk in chunks:
        files_text.append(f"\n\n--- FILE: {chunk.path} ---\n{chunk.content}")

    return f"""
You are NOVA, the Universal Dragon architecture reviewer.

Project root: {root}
AI provider: {AI_PROVIDER}
Model: {DEFAULT_MODEL}

Review these project files safely. Focus on practical engineering only.

Return a Markdown report with these sections:
1. Universal Dragon summary
2. Current architecture map
3. Problems found
4. Missing safety pieces
5. Error handling and rollback checklist
6. Privacy/security risks to avoid
7. Best next 10 improvements, step by step
8. Files that should be cleaned, moved, or renamed
9. Final short plan for Aslam

Important rules:
- Do not suggest harmful hacking, malware, tracking people, stealing data, or bypassing real systems.
- Do not expose or ask for secrets/API keys.
- Prefer defensive security, diagnostics, logs, rollback, approval, and safe automation.
- Keep the project identity: Universal Dragon, Aslam, NOVA Core, EVE System.
- Be direct and practical.

Project files:
{''.join(files_text)}
""".strip()


def extract_text(response: object) -> str:
    output_text = getattr(response, "output_text", None)
    if output_text:
        return str(output_text)
    try:
        choices = getattr(response, "choices")
        return choices[0].message.content or ""
    except Exception:
        return str(response)


def call_groq(prompt: str) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise SystemExit(
            "GROQ_API_KEY is missing. Set it first:\n"
            "  export GROQ_API_KEY=\"your_groq_api_key_here\""
        )

    client = OpenAI(api_key=api_key, base_url=GROQ_BASE_URL)
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": "You are NOVA, a safe Universal Dragon project architecture reviewer."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    return extract_text(response)


def call_openai(prompt: str) -> str:
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit(
            "OPENAI_API_KEY is missing. Set it first:\n"
            "  export OPENAI_API_KEY=\"your_openai_api_key_here\""
        )

    client = OpenAI()
    if hasattr(client, "responses"):
        response = client.responses.create(
            model=OPENAI_MODEL,
            input=[
                {"role": "system", "content": "You are NOVA, a safe Universal Dragon project architecture reviewer."},
                {"role": "user", "content": prompt},
            ],
        )
        return extract_text(response)

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are NOVA, a safe Universal Dragon project architecture reviewer."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    return extract_text(response)


def call_ai(prompt: str) -> str:
    if AI_PROVIDER == "groq":
        return call_groq(prompt)
    if AI_PROVIDER == "openai":
        return call_openai(prompt)
    raise SystemExit(
        f"Unsupported AI_PROVIDER: {AI_PROVIDER}\n"
        "Use one of:\n"
        "  export AI_PROVIDER=\"groq\"\n"
        "  export AI_PROVIDER=\"openai\""
    )


def main() -> None:
    root = Path(sys.argv[1]).expanduser().resolve() if len(sys.argv) > 1 else Path.cwd().resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Project folder not found: {root}")

    print("🐉 Universal Dragon analyzer")
    print(f"📁 Project: {root}")
    print(f"🔌 Provider: {AI_PROVIDER}")
    print(f"🧠 Model: {DEFAULT_MODEL}")
    print("🔎 Reading safe source files...")

    chunks = read_project_files(root)
    if not chunks:
        raise SystemExit("No readable source files found.")

    print(f"✅ Files included: {len(chunks)}")
    prompt = build_prompt(root, chunks)

    print("🚀 Sending architecture review request...")
    try:
        report = call_ai(prompt)
    except Exception as exc:
        message = str(exc)
        if "model" in message.lower() and ("not" in message.lower() or "found" in message.lower()):
            message += (
                "\n\nModel access problem. Try setting a model your provider supports:\n"
                "  export GROQ_MODEL=\"openai/gpt-oss-120b\"\n"
                "  export OPENAI_MODEL=\"your_available_openai_model_name\""
            )
        raise SystemExit(message) from exc

    out_dir = root / "reports"
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / "universal_dragon_analysis.md"
    out_file.write_text(report, encoding="utf-8")

    print(f"✅ Report saved: {out_file}")
    print("\n--- REPORT PREVIEW ---\n")
    print(report[:3000])
    if len(report) > 3000:
        print("\n[Preview truncated. Open the full Markdown report file.] ")


if __name__ == "__main__":
    main()
