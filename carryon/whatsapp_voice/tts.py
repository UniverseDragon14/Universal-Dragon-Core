#!/usr/bin/env python3
"""Text-to-Speech adapters for the WhatsApp voice engine.

Produces a WAV file from reply text. The engine then transcodes that WAV to
opus/ogg for WhatsApp PTT delivery via ffmpeg. Select with CARRYON_TTS_BACKEND:
  - "piper" : shells out to the local piper binary (great on ARM64 / Pi5)
  - "espeak": espeak-ng fallback (tiny, always available in Termux)
  - "stub"  : writes 300ms of silence (wiring/test mode)
"""
from __future__ import annotations

import os
import subprocess
import wave

from carryon.common.log import get_logger

MARKER = "CARRYON_WA_TTS_V01"
VERSION = "0.1.0"

log = get_logger("wa.tts")


def _piper(text: str, out_wav: str) -> None:
    binary = os.environ.get("PIPER_BIN", "piper")
    model = os.environ.get("PIPER_MODEL", "models/en_US-amy-medium.onnx")
    cmd = [binary, "--model", model, "--output_file", out_wav]
    log.info("tts piper start", model=model)
    subprocess.run(cmd, input=text.encode("utf-8"), check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _espeak(text: str, out_wav: str) -> None:
    binary = os.environ.get("ESPEAK_BIN", "espeak-ng")
    voice = os.environ.get("ESPEAK_VOICE", "en")
    cmd = [binary, "-v", voice, "-w", out_wav, text]
    log.info("tts espeak start", voice=voice)
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _stub(_text: str, out_wav: str) -> None:
    with wave.open(out_wav, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(b"\x00\x00" * 4800)  # ~0.3s silence
    log.warn("tts stub backend active")


def synthesize(text: str, out_wav: str) -> str:
    backend = os.environ.get("CARRYON_TTS_BACKEND", "stub").lower()
    try:
        if backend == "piper":
            _piper(text, out_wav)
        elif backend == "espeak":
            _espeak(text, out_wav)
        else:
            _stub(text, out_wav)
    except Exception as exc:
        log.error("tts failed, writing silence", backend=backend, error=str(exc))
        _stub(text, out_wav)
    return out_wav
