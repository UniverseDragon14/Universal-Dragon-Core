#!/usr/bin/env python3
"""LLM context bridge for the WhatsApp voice engine.

Turns a recognized utterance + light session memory into a reply string.
Backends (CARRYON_LLM_BACKEND):
  - "gemini" : Google Gemini via GEMINI_API_KEY (matches repo .env.example)
  - "http"   : POST to a local model server (Ollama-compatible /api/chat)
  - "echo"   : deterministic offline reply (wiring/test mode)

Kept transport-agnostic on purpose: no network import at module load, so the
engine still boots on an offline Pi5 and simply uses the echo backend.
"""
from __future__ import annotations

import json
import os
import urllib.request

from carryon.common.log import get_logger

MARKER = "CARRYON_WA_LLM_V01"
VERSION = "0.1.0"

log = get_logger("wa.llm")

SYSTEM_PROMPT = os.environ.get(
    "CARRYON_LLM_SYSTEM",
    "You are Nova, the Universal Dragon voice assistant. Reply briefly and "
    "warmly in the same language the user spoke. Keep replies under 40 words "
    "so they sound natural as a voice note.",
)


def _gemini(utterance: str, history: list[dict]) -> str:
    api_key = os.environ["GEMINI_API_KEY"]
    model = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={api_key}"
    )
    contents = [{"role": "user", "parts": [{"text": SYSTEM_PROMPT}]}]
    for turn in history[-6:]:
        contents.append({"role": turn["role"], "parts": [{"text": turn["text"]}]})
    contents.append({"role": "user", "parts": [{"text": utterance}]})
    body = json.dumps({"contents": contents}).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    return data["candidates"][0]["content"]["parts"][0]["text"].strip()


def _http(utterance: str, history: list[dict]) -> str:
    url = os.environ.get("CARRYON_LLM_URL", "http://127.0.0.1:11434/api/chat")
    model = os.environ.get("CARRYON_LLM_MODEL", "llama3.2")
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for turn in history[-6:]:
        role = "assistant" if turn["role"] == "model" else "user"
        messages.append({"role": role, "content": turn["text"]})
    messages.append({"role": "user", "content": utterance})
    body = json.dumps({"model": model, "messages": messages, "stream": False}).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read())
    return data["message"]["content"].strip()


def reply(utterance: str, history: list[dict] | None = None) -> str:
    history = history or []
    backend = os.environ.get("CARRYON_LLM_BACKEND", "echo").lower()
    if not utterance.strip():
        return "Sorry, I could not hear that clearly. Please say it again."
    try:
        if backend == "gemini":
            return _gemini(utterance, history)
        if backend == "http":
            return _http(utterance, history)
        log.warn("llm echo backend active", backend=backend)
        return f"You said: {utterance}"
    except Exception as exc:
        log.error("llm failed", backend=backend, error=str(exc))
        return "I hit a problem reaching my brain just now. Try again in a moment."
