#!/usr/bin/env python3
"""Speech-to-Text adapters for the WhatsApp voice engine.

Pluggable backends so the same engine runs on a Pi5 (faster-whisper) or a
phone in Termux (whisper.cpp binary). Select with CARRYON_STT_BACKEND:
  - "whisper_cpp"     : shells out to a local whisper.cpp `main` binary
  - "faster_whisper"  : uses the faster-whisper python package
  - "stub"            : returns empty text (wiring/test mode)

All backends take a path to a mono 16kHz WAV and return recognized text.
Audio decoding (opus/ogg -> wav) is handled by ffmpeg in the engine, not here.
"""
from __future__ import annotations

import os
import subprocess

from carryon.common.log import get_logger

MARKER = "CARRYON_WA_STT_V01"
VERSION = "0.1.0"

log = get_logger("wa.stt")


def _whisper_cpp(wav_path: str) -> str:
    binary = os.environ.get("WHISPER_CPP_BIN", "whisper-cpp")
    model = os.environ.get("WHISPER_CPP_MODEL", "models/ggml-base.bin")
    # -otxt writes <wav>.txt; -nt strips timestamps; -l auto detects language.
    cmd = [binary, "-m", model, "-f", wav_path, "-otxt", "-nt", "-l", "auto"]
    log.info("stt whisper.cpp start", cmd=cmd)
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    txt_path = wav_path + ".txt"
    if not os.path.exists(txt_path):
        return ""
    with open(txt_path, "r", encoding="utf-8") as fh:
        return fh.read().strip()


def _faster_whisper(wav_path: str) -> str:
    from faster_whisper import WhisperModel  # imported lazily

    model_name = os.environ.get("FASTER_WHISPER_MODEL", "base")
    device = os.environ.get("FASTER_WHISPER_DEVICE", "cpu")
    compute = os.environ.get("FASTER_WHISPER_COMPUTE", "int8")
    log.info("stt faster-whisper start", model=model_name, device=device)
    model = WhisperModel(model_name, device=device, compute_type=compute)
    segments, _info = model.transcribe(wav_path, vad_filter=True)
    return " ".join(seg.text.strip() for seg in segments).strip()


def transcribe(wav_path: str) -> str:
    backend = os.environ.get("CARRYON_STT_BACKEND", "stub").lower()
    try:
        if backend == "whisper_cpp":
            return _whisper_cpp(wav_path)
        if backend == "faster_whisper":
            return _faster_whisper(wav_path)
        log.warn("stt stub backend active", backend=backend)
        return ""
    except Exception as exc:  # keep the engine alive; log and yield empty text
        log.error("stt failed", backend=backend, error=str(exc))
        return ""
