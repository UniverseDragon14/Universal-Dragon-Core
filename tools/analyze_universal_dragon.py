#!/usr/bin/env python3
"""
Universal Dragon / NOVA Project Analyzer

Safe architecture review tool for Universal Dragon project folders.
- No API key is stored in this file.
- Reads selected public/source files only.
- Skips secrets, env files, virtualenvs, node_modules, git folders, logs, and large binaries.
- Writes a local Markdown report.

Usage:
  export OPENAI_API_KEY="your_api_key_here"
  export OPENAI_MODEL="gpt-5.5"   # Change if your Platform account uses another model name
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
    raise SystemExit(
        "OpenAI Python package not installed. Run: pip install openai"
    ) from exc


DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.5")
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
    # OpenAI / common API keys
    (re.compile(r"sk-[A-Za-z0-9_\-]{20,}"), "sk-***REDACTED***"),
    (re.compile(r"sk-proj-[A-Za-z0-9_\-]{20,}"), "sk-proj-***REDACTED***"),
    # Generic assignment style secrets
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
        # Allow .env.example because it is normally a safe template.
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

        part = FileChunk(path=path.relative_to(root), content=raw)
        chunks.append(part)
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

    # Fallback for older SDK response shapes.
    try:
        choices = getattr(response, "choices")
        return choices[0].message.content
    except Exception:
        return str(response)


def call_openai(prompt: str) -> str:
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit(
            "OPENAI_API_KEY is missing. Set it first:\n"
            "  export OPENAI_API_KEY=\"your_api_key_here\""
        )

    client = OpenAI()

    # Newer OpenAI SDK path: Responses API.
    if hasattr(client, "responses"):
        response = client.responses.create(
            model=DEFAULT_MODEL,
            input=[
                {
                    "role": "system",
                    "content": "You are NOVA, a safe Universal Dragon project architecture reviewer."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
        )
        return extract_text(response)

    # Compatibility fallback for older SDK versions.
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are NOVA, a safe Universal Dragon project architecture reviewer."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
    )
    return extract_text(response)


def main() -> None:
    root = Path(sys.argv[1]).expanduser().resolve() if len(sys.argv) > 1 else Path.cwd().resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Project folder not found: {root}")

    print(f"🐉 Universal Dragon analyzer")
    print(f"📁 Project: {root}")
    print(f"🧠 Model: {DEFAULT_MODEL}")
    print("🔎 Reading safe source files...")

    chunks = read_project_files(root)
    if not chunks:
        raise SystemExit("No readable source files found.")

    print(f"✅ Files included: {len(chunks)}")
    prompt = build_prompt(root, chunks)

    print("🚀 Sending architecture review request...")
    try:
        report = call_openai(prompt)
    except Exception as exc:
        message = str(exc)
        if "model" in message.lower() and ("not" in message.lower() or "found" in message.lower()):
            message += (
                "\n\nModel access problem. Try setting a model your OpenAI Platform account supports:\n"
                "  export OPENAI_MODEL=\"your_available_model_name\""
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
