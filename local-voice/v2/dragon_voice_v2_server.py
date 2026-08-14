from __future__ import annotations

import hmac
import importlib.util
import io
import json
import os
import threading
import time
import urllib.error
import urllib.request
import wave
from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field, field_validator

from voice_soul_v2 import CONTEXTS, MOODS, REACTIONS, plan_voice

APP_DIR = Path(__file__).resolve().parent
PROFILES_PATH = Path(os.environ.get("DRAGON_V2_PROFILES", APP_DIR / "profiles-v2.json")).expanduser().resolve()
REFERENCE_DIR = Path(os.environ.get("DRAGON_V2_REFERENCE_DIR", APP_DIR / "references")).expanduser().resolve()
ACCESS_TOKEN = os.environ.get("DRAGON_VOICE_TOKEN", "")
V1_URL = os.environ.get("DRAGON_V1_URL", "http://127.0.0.1:8123").rstrip("/")
MAX_TEXT_CHARS = int(os.environ.get("DRAGON_VOICE_MAX_TEXT", "1200"))
ALLOW_NANO_WITHOUT_REFERENCE = os.environ.get("DRAGON_V2_ALLOW_NANO_WITHOUT_REFERENCE", "0") == "1"

app = FastAPI(title="Universal Dragon Human Voice Soul", version="2.0.0")
_engine_lock = threading.Lock()
_synthesis_lock = threading.Lock()
_kokoro_model: Any | None = None
_kokoro_pipelines: dict[str, Any] = {}
_nano_model: Any | None = None


def _authorized(authorization: str | None) -> bool:
    """Validate the local bearer token and fail closed when it is absent."""
    if not ACCESS_TOKEN:
        return False
    if not authorization or not authorization.lower().startswith("bearer "):
        return False
    candidate = authorization.split(" ", 1)[1].strip()
    return bool(candidate) and hmac.compare_digest(candidate, ACCESS_TOKEN)


def _require_auth(authorization: str | None) -> None:
    """Require a valid local bearer token."""
    if not _authorized(authorization):
        raise HTTPException(status_code=401, detail="unauthorized", headers={"WWW-Authenticate": "Bearer"})


def _module_ready(name: str) -> bool:
    """Check whether an optional local engine module is installed without loading it."""
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, ValueError):
        return False


def _reference_path(filename: str) -> Path:
    """Resolve a local reference WAV without allowing path traversal."""
    if not filename or Path(filename).name != filename:
        raise RuntimeError("invalid reference filename")
    base = REFERENCE_DIR.resolve()
    path = (base / filename).resolve()
    if path.parent != base:
        raise RuntimeError("reference path escaped directory")
    return path


def _pcm16_wav(audio: Any, sample_rate: int) -> bytes:
    """Convert a mono floating-point tensor/array into a standard PCM16 WAV."""
    import numpy as np

    if hasattr(audio, "detach"):
        audio = audio.detach().cpu().numpy()
    values = np.asarray(audio, dtype=np.float32).reshape(-1)
    if values.size == 0:
        raise RuntimeError("engine returned empty audio")
    values = np.nan_to_num(values, nan=0.0, posinf=1.0, neginf=-1.0)
    pcm = (np.clip(values, -1.0, 1.0) * 32767.0).astype("<i2")
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(int(sample_rate))
        wav_file.writeframes(pcm.tobytes())
    return buffer.getvalue()


def _kokoro_engine(plan: dict[str, Any]) -> tuple[bytes, dict[str, str]]:
    """Synthesize with the lightweight multi-voice Kokoro CPU engine."""
    global _kokoro_model

    if not _module_ready("kokoro"):
        raise RuntimeError("kokoro_not_installed")

    from kokoro import KModel, KPipeline
    import numpy as np

    voice_id = str(plan["kokoro"]["voice"])
    lang_code = "b" if voice_id.startswith("bf_") or voice_id.startswith("bm_") else "a"

    with _engine_lock:
        if _kokoro_model is None:
            _kokoro_model = KModel(repo_id="hexgrad/Kokoro-82M").to("cpu").eval()
        pipeline = _kokoro_pipelines.get(lang_code)
        if pipeline is None:
            pipeline = KPipeline(lang_code=lang_code, repo_id="hexgrad/Kokoro-82M", model=_kokoro_model)
            _kokoro_pipelines[lang_code] = pipeline

    chunks: list[Any] = []
    for _, _, audio in pipeline(
        plan["spoken_text"],
        voice=voice_id,
        speed=float(plan["kokoro"]["speed"]),
    ):
        if audio is not None:
            if hasattr(audio, "detach"):
                audio = audio.detach().cpu().numpy()
            chunks.append(np.asarray(audio, dtype=np.float32).reshape(-1))

    if not chunks:
        raise RuntimeError("kokoro_empty_audio")

    joined = np.concatenate(chunks)
    return _pcm16_wav(joined, 24000), {"voice": voice_id, "reference": "builtin"}


def _nano_engine(plan: dict[str, Any]) -> tuple[bytes, dict[str, str]]:
    """Synthesize with optional Chatterbox Nano and a permitted local reference when available."""
    global _nano_model

    if not _module_ready("chatterbox"):
        raise RuntimeError("nano_not_installed")

    from chatterbox.tts_turbo import ChatterboxTurboTTS

    reference_name = str(plan["nano"]["reference_file"])
    reference = _reference_path(reference_name)
    use_reference = reference.is_file()
    if not use_reference and not ALLOW_NANO_WITHOUT_REFERENCE:
        raise RuntimeError("nano_reference_missing")

    with _engine_lock:
        if _nano_model is None:
            _nano_model = ChatterboxTurboTTS.from_pretrained(device="cpu", nano=True)
        model = _nano_model

    kwargs: dict[str, Any] = {}
    if use_reference:
        kwargs["audio_prompt_path"] = str(reference)
    audio = model.generate(str(plan["nano"]["text"]), **kwargs)
    return _pcm16_wav(audio, int(model.sr)), {
        "voice": "reference" if use_reference else "nano-default",
        "reference": "yes" if use_reference else "no",
    }


def _piper_engine(plan: dict[str, Any]) -> tuple[bytes, dict[str, str]]:
    """Fall back to the already-proven local Piper V1 service."""
    if not ACCESS_TOKEN:
        raise RuntimeError("local_token_missing")
    payload = json.dumps(
        {
            "text": plan["spoken_text"],
            "profile": plan["piper"]["profile"],
            "intensity": plan["intensity"],
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        f"{V1_URL}/v1/speak",
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            audio = response.read()
            model = response.headers.get("X-Dragon-Voice-Model", "piper")
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"piper_http_{exc.code}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError("piper_unreachable") from exc
    if not audio.startswith(b"RIFF"):
        raise RuntimeError("piper_invalid_wav")
    return audio, {"voice": model, "reference": "none"}


class SpeakV2Request(BaseModel):
    """Bounded Human Voice Soul V2 request."""

    text: str = Field(min_length=1, max_length=MAX_TEXT_CHARS)
    profile: str | None = None
    mood: str | None = None
    context: str = "chat"
    reaction: str | None = None
    intensity: float = Field(default=0.65, ge=0.0, le=1.0)
    engine: Literal["auto", "kokoro", "nano", "piper"] = "auto"

    @field_validator("text")
    @classmethod
    def non_blank_text(cls, value: str) -> str:
        """Reject whitespace-only speech text."""
        stripped = value.strip()
        if not stripped:
            raise ValueError("text must contain non-whitespace characters")
        return stripped

    @field_validator("context")
    @classmethod
    def known_context(cls, value: str) -> str:
        """Normalize unknown contexts to chat rather than permitting arbitrary controls."""
        normalized = value.strip().lower()
        return normalized if normalized in CONTEXTS else "chat"

    @field_validator("mood", "reaction")
    @classmethod
    def bounded_optional_control(cls, value: str | None, info: Any) -> str | None:
        """Drop unsupported mood/reaction control names."""
        if value is None:
            return None
        normalized = value.strip().lower()
        allowed = MOODS if info.field_name == "mood" else REACTIONS
        return normalized if normalized in allowed else None


@app.get("/health")
def health() -> dict[str, Any]:
    """Report installed engines without loading their neural weights."""
    references = 0
    if REFERENCE_DIR.is_dir():
        references = sum(1 for path in REFERENCE_DIR.glob("*.wav") if path.is_file())
    return {
        "ok": True,
        "schema": "dragon.voice-soul.health.v2",
        "auth_configured": bool(ACCESS_TOKEN),
        "kokoro_installed": _module_ready("kokoro"),
        "nano_installed": _module_ready("chatterbox"),
        "piper_v1_fallback": V1_URL,
        "reference_voice_count": references,
        "profile_count": 7,
        "paid_api_required": False,
        "device_claim": "cpu-first",
        "v3d_tts_inference_claimed": False,
    }


@app.post("/v2/plan")
def plan_endpoint(request: SpeakV2Request, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    """Return the sanitized provider-independent execution plan."""
    _require_auth(authorization)
    return plan_voice(
        request.text,
        profile=request.profile,
        mood=request.mood,
        context=request.context,
        reaction=request.reaction,
        intensity=request.intensity,
        profiles_path=PROFILES_PATH,
    )


@app.get("/v2/profiles")
def profiles_endpoint(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    """Return the seven non-secret voice identities and reference readiness."""
    _require_auth(authorization)
    data = json.loads(PROFILES_PATH.read_text(encoding="utf-8"))
    result = []
    for profile_id, profile in data["profiles"].items():
        reference = _reference_path(str(profile["reference_file"]))
        result.append(
            {
                "id": profile_id,
                "display_name": profile["display_name"],
                "persona": profile["persona"],
                "kokoro_voice": profile["kokoro_voice"],
                "reference_ready": reference.is_file(),
            }
        )
    return {"schema": "dragon.voice-soul.profile-list.v2", "profiles": result}


@app.post("/v2/speak")
def speak_endpoint(request: SpeakV2Request, authorization: str | None = Header(default=None)) -> Response:
    """Generate Human Voice Soul audio with truthful engine fallback markers."""
    _require_auth(authorization)
    plan = plan_voice(
        request.text,
        profile=request.profile,
        mood=request.mood,
        context=request.context,
        reaction=request.reaction,
        intensity=request.intensity,
        profiles_path=PROFILES_PATH,
    )

    requested = request.engine
    engine_order = [requested] if requested != "auto" else list(plan["engine_order"])
    engines = {"kokoro": _kokoro_engine, "nano": _nano_engine, "piper": _piper_engine}
    failures: list[str] = []
    started = time.perf_counter()

    with _synthesis_lock:
        for engine_name in engine_order:
            try:
                audio, meta = engines[engine_name](plan)
                elapsed_ms = int((time.perf_counter() - started) * 1000)
                return Response(
                    content=audio,
                    media_type="audio/wav",
                    headers={
                        "Cache-Control": "no-store",
                        "X-Dragon-Voice-Schema": "dragon.voice-soul.v2",
                        "X-Dragon-Voice-Engine": engine_name,
                        "X-Dragon-Voice-Profile": str(plan["profile"]),
                        "X-Dragon-Voice-Mood": str(plan["mood"]),
                        "X-Dragon-Voice-Reaction": str(plan["reaction"]),
                        "X-Dragon-Voice-Reference": meta["reference"],
                        "X-Dragon-Voice-Model": meta["voice"],
                        "X-Dragon-Engine-Fallback": "yes" if engine_name != engine_order[0] else "no",
                        "X-Dragon-Inference-Ms": str(elapsed_ms),
                        "X-Dragon-Paid-API": "no",
                        "X-Dragon-Device-Claim": "cpu-first",
                        "X-Dragon-V3D-TTS": "not-claimed",
                    },
                )
            except Exception as exc:
                failures.append(f"{engine_name}:{type(exc).__name__}")
                if requested != "auto":
                    break

    raise HTTPException(
        status_code=503,
        detail={"error": "all_local_voice_engines_failed", "engines": failures},
    )
