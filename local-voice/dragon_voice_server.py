from __future__ import annotations

import hmac
import io
import json
import os
import threading
import time
import wave
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field
from piper import PiperVoice, SynthesisConfig

APP_DIR = Path(__file__).resolve().parent
MODEL_DIR = Path(os.environ.get("DRAGON_VOICE_MODEL_DIR", APP_DIR / "models")).expanduser().resolve()
PROFILES_PATH = Path(os.environ.get("DRAGON_VOICE_PROFILES", APP_DIR / "profiles.json")).expanduser().resolve()
ACCESS_TOKEN = os.environ.get("DRAGON_VOICE_TOKEN", "")
MAX_TEXT_CHARS = int(os.environ.get("DRAGON_VOICE_MAX_TEXT", "1200"))

app = FastAPI(title="Universal Dragon Local Voice", version="1.0.0")
_cache_lock = threading.Lock()
_synthesis_lock = threading.Lock()
_voice_cache: dict[str, PiperVoice] = {}


def _load_profiles() -> dict[str, Any]:
    data = json.loads(PROFILES_PATH.read_text(encoding="utf-8"))
    if data.get("schema") != "dragon.local-voice.profiles.v1":
        raise RuntimeError("unsupported voice profile schema")
    profiles = data.get("profiles")
    if not isinstance(profiles, dict) or not profiles:
        raise RuntimeError("voice profiles missing")
    if data.get("default_profile") not in profiles:
        raise RuntimeError("default profile missing")
    return data


PROFILES = _load_profiles()


def _authorized(authorization: str | None) -> bool:
    if not ACCESS_TOKEN:
        return True
    if not authorization or not authorization.lower().startswith("bearer "):
        return False
    candidate = authorization.split(" ", 1)[1].strip()
    return bool(candidate) and hmac.compare_digest(candidate, ACCESS_TOKEN)


def _require_auth(authorization: str | None) -> None:
    if not _authorized(authorization):
        raise HTTPException(status_code=401, detail="unauthorized", headers={"WWW-Authenticate": "Bearer"})


def _safe_model_path(filename: str) -> Path:
    if not filename or Path(filename).name != filename:
        raise RuntimeError("invalid model filename")
    path = (MODEL_DIR / filename).resolve()
    if path.parent != MODEL_DIR:
        raise RuntimeError("model path escaped model directory")
    return path


def _resolve_profile(name: str) -> tuple[str, dict[str, Any]]:
    profiles: dict[str, Any] = PROFILES["profiles"]
    selected = name if name in profiles else PROFILES["default_profile"]
    return selected, profiles[selected]


def _get_voice(profile: dict[str, Any]) -> tuple[PiperVoice, Path, bool]:
    requested = _safe_model_path(str(profile["model"]))
    fallback = False
    model_path = requested

    if not model_path.is_file():
        model_path = _safe_model_path(str(PROFILES["default_model"]))
        fallback = True

    if not model_path.is_file():
        raise HTTPException(
            status_code=503,
            detail=f"voice model unavailable: {requested.name}; bootstrap model missing: {model_path.name}",
        )

    key = str(model_path)
    with _cache_lock:
        voice = _voice_cache.get(key)
        if voice is None:
            voice = PiperVoice.load(key)
            _voice_cache[key] = voice
    return voice, model_path, fallback


def _synthesis_config(profile: dict[str, Any], intensity: float) -> SynthesisConfig:
    intensity = max(0.0, min(1.0, intensity))
    base_noise = float(profile.get("noise_scale", 0.667))
    base_width = float(profile.get("noise_w_scale", 0.8))
    # Keep profile character bounded. Intensity only nudges variation, never model identity.
    noise_scale = max(0.1, min(1.5, base_noise * (0.9 + 0.2 * intensity)))
    noise_w_scale = max(0.1, min(1.5, base_width * (0.9 + 0.2 * intensity)))
    return SynthesisConfig(
        volume=float(profile.get("volume", 1.0)),
        length_scale=float(profile.get("length_scale", 1.0)),
        noise_scale=noise_scale,
        noise_w_scale=noise_w_scale,
        normalize_audio=True,
    )


class SpeakRequest(BaseModel):
    text: str = Field(min_length=1, max_length=MAX_TEXT_CHARS)
    profile: str = "nova_warm"
    intensity: float = Field(default=0.65, ge=0.0, le=1.0)


@app.get("/health")
def health() -> dict[str, Any]:
    profiles: dict[str, Any] = PROFILES["profiles"]
    installed = []
    for name, profile in profiles.items():
        try:
            present = _safe_model_path(str(profile["model"])).is_file()
        except RuntimeError:
            present = False
        installed.append({"profile": name, "dedicated_model": present})

    default_path = _safe_model_path(str(PROFILES["default_model"]))
    return {
        "ok": True,
        "schema": "dragon.local-voice.health.v1",
        "engine": "piper",
        "backend": "onnxruntime",
        "device_claim": "cpu-baseline",
        "v3d_voice_inference_claimed": False,
        "profile_count": len(profiles),
        "default_model_ready": default_path.is_file(),
        "profiles": installed,
        "paid_api_required": False,
    }


@app.get("/v1/profiles")
def list_profiles(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    _require_auth(authorization)
    public_profiles = []
    for name, profile in PROFILES["profiles"].items():
        public_profiles.append(
            {
                "id": name,
                "display_name": profile["display_name"],
                "character": profile["character"],
                "dedicated_model_ready": _safe_model_path(str(profile["model"])).is_file(),
            }
        )
    return {
        "schema": "dragon.local-voice.profile-list.v1",
        "default_profile": PROFILES["default_profile"],
        "profiles": public_profiles,
    }


@app.post("/v1/speak")
def speak(request: SpeakRequest, authorization: str | None = Header(default=None)) -> Response:
    _require_auth(authorization)
    profile_name, profile = _resolve_profile(request.profile)
    voice, model_path, fallback = _get_voice(profile)
    syn_config = _synthesis_config(profile, request.intensity)

    started = time.perf_counter()
    buffer = io.BytesIO()
    with _synthesis_lock:
        with wave.open(buffer, "wb") as wav_file:
            voice.synthesize_wav(request.text.strip(), wav_file, syn_config=syn_config)
    elapsed_ms = int((time.perf_counter() - started) * 1000)

    return Response(
        content=buffer.getvalue(),
        media_type="audio/wav",
        headers={
            "Cache-Control": "no-store",
            "X-Dragon-Voice-Profile": profile_name,
            "X-Dragon-Voice-Model": model_path.name,
            "X-Dragon-Model-Fallback": "yes" if fallback else "no",
            "X-Dragon-Inference-Ms": str(elapsed_ms),
            "X-Dragon-Paid-API": "no",
            "X-Dragon-Device-Claim": "cpu-baseline",
        },
    )
