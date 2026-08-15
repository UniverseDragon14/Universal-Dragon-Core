from __future__ import annotations

import threading
from types import SimpleNamespace
from typing import Any

import numpy as np
import torch
from huggingface_hub import hf_hub_download
from kokoro.model import KModel
from misaki.espeak import EspeakFallback

_REPO_ID = "hexgrad/Kokoro-82M"
_model: KModel | None = None
_voice_packs: dict[str, torch.Tensor] = {}
_g2p: dict[bool, EspeakFallback] = {}
_lock = threading.Lock()


def _chunks(text: str, limit: int = 220) -> list[str]:
    """Split bounded text into small chunks so raw phonemes stay under model limits."""
    words = text.split()
    out: list[str] = []
    current: list[str] = []
    size = 0
    for word in words:
        extra = len(word) + (1 if current else 0)
        if current and size + extra > limit:
            out.append(" ".join(current))
            current = [word]
            size = len(word)
        else:
            current.append(word)
            size += extra
    if current:
        out.append(" ".join(current))
    return out


def _get_model() -> KModel:
    global _model
    with _lock:
        if _model is None:
            _model = KModel(repo_id=_REPO_ID).to("cpu").eval()
        return _model


def _get_voice_pack(voice_id: str) -> torch.Tensor:
    with _lock:
        pack = _voice_packs.get(voice_id)
        if pack is None:
            path = hf_hub_download(repo_id=_REPO_ID, filename=f"voices/{voice_id}.pt")
            pack = torch.load(path, map_location="cpu", weights_only=True)
            _voice_packs[voice_id] = pack
        return pack


def _get_g2p(british: bool) -> EspeakFallback:
    with _lock:
        g2p = _g2p.get(british)
        if g2p is None:
            g2p = EspeakFallback(british=british)
            _g2p[british] = g2p
        return g2p


def synthesize(text: str, voice_id: str, speed: float) -> tuple[np.ndarray, dict[str, str]]:
    """Run Kokoro KModel with spaCy-free eSpeak English phonemes on CPU."""
    british = voice_id.startswith("bf_") or voice_id.startswith("bm_")
    model = _get_model()
    pack = _get_voice_pack(voice_id)
    g2p = _get_g2p(british)

    pieces: list[np.ndarray] = []
    for chunk in _chunks(text):
        phonemes, _ = g2p(SimpleNamespace(text=chunk))
        phonemes = (phonemes or "").strip()
        if not phonemes:
            continue
        if len(phonemes) > 500:
            raise RuntimeError("kokoro_phoneme_chunk_too_long")

        style_index = min(max(len(phonemes) - 1, 0), int(pack.shape[0]) - 1)
        audio = model(phonemes, pack[style_index], speed=float(speed))
        values = audio.detach().cpu().numpy().astype(np.float32, copy=False).reshape(-1)
        if values.size:
            pieces.append(values)
            pieces.append(np.zeros(1440, dtype=np.float32))  # 60 ms at 24 kHz

    if not pieces:
        raise RuntimeError("kokoro_empty_audio")

    joined = np.concatenate(pieces[:-1] if len(pieces) > 1 else pieces)
    return joined, {
        "voice": voice_id,
        "reference": "builtin",
        "g2p": "espeak-spacy-free",
    }
