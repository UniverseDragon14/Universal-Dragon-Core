from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

APP_DIR = Path(__file__).resolve().parent
DEFAULT_PROFILES_PATH = APP_DIR / "profiles-v2.json"

MOODS = {
    "neutral",
    "smile",
    "laugh",
    "serious",
    "whisper",
    "sad",
    "confident",
    "curious",
    "alert",
}
CONTEXTS = {"chat", "whatsapp", "wake", "story", "robot", "alert", "night"}
REACTIONS = {"none", "laugh", "chuckle", "cough", "sigh", "gasp", "breath", "throat_clear"}
NANO_NATIVE_TAGS = {"laugh": "[laugh]", "chuckle": "[chuckle]", "cough": "[cough]"}


def load_profiles(path: Path = DEFAULT_PROFILES_PATH) -> dict[str, Any]:
    """Load the V2 voice identity contract."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != "dragon.voice-soul.profiles.v2":
        raise RuntimeError("unsupported V2 profile schema")
    profiles = data.get("profiles")
    if not isinstance(profiles, dict) or len(profiles) != 7:
        raise RuntimeError("V2 requires exactly seven voice profiles")
    if data.get("default_profile") not in profiles:
        raise RuntimeError("V2 default profile missing")
    return data


def sanitize_spoken_text(text: str, limit: int = 1200) -> str:
    """Remove private-reasoning markup and untrusted audio tags from speech."""
    value = text
    value = re.sub(r"<(think|analysis|reasoning)\b[^>]*>[\s\S]*?</\1>", " ", value, flags=re.I)
    value = re.sub(r"<(think|analysis|reasoning)\b[^>]*>[\s\S]*$", " ", value, flags=re.I)
    value = re.sub(r"\[[^\]]{1,80}\]", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value[:limit].strip()


def infer_mood(text: str, context: str) -> str:
    """Infer a conservative delivery mood from bounded text and context."""
    lower = text.lower()
    if context == "alert" or re.search(r"\b(error|danger|warning|critical|stop|urgent)\b", lower):
        return "alert"
    if context == "night" or re.search(r"\b(whisper|quiet|softly|sleep|night)\b", lower):
        return "whisper"
    if re.search(r"\b(haha|hehe|lol|hilarious|funny)\b", lower):
        return "laugh"
    if re.search(r"\b(sad|sorry|miss|hurt|unfortunately)\b", lower):
        return "sad"
    if re.search(r"\b(why|how|wonder|curious|really\?)\b", lower):
        return "curious"
    if context == "wake" or re.search(r"\b(hey dragon|wake|awaken|resonance)\b", lower):
        return "smile"
    if context == "robot":
        return "confident"
    return "neutral"


def choose_profile(profiles: dict[str, Any], requested: str | None, mood: str, context: str) -> str:
    """Choose a stable identity while respecting explicit valid requests."""
    available = profiles["profiles"]
    if requested and requested in available:
        return requested
    if context == "whatsapp":
        return "whatsapp_natural"
    if context == "story":
        return "story_soul"
    if context == "night" or mood == "whisper":
        return "night_whisper"
    if context == "alert" or mood in {"serious", "alert"}:
        return "dragon_serious"
    if context == "robot" or mood == "confident":
        return "dragon_deep"
    if mood in {"smile", "laugh"}:
        return "dragon_playful"
    return profiles["default_profile"]


def _reaction_for(mood: str, requested: str | None) -> str:
    """Resolve a reaction without accepting arbitrary model control tokens."""
    if requested in REACTIONS:
        return requested
    if mood == "laugh":
        return "laugh"
    if mood == "smile":
        return "chuckle"
    if mood == "sad":
        return "sigh"
    if mood == "whisper":
        return "breath"
    return "none"


def _speed_for(base: float, mood: str, intensity: float) -> float:
    """Apply bounded pacing adjustments for natural delivery."""
    intensity = max(0.0, min(1.0, intensity))
    factor = {
        "neutral": 1.0,
        "smile": 1.02,
        "laugh": 1.04,
        "serious": 0.94,
        "whisper": 0.88,
        "sad": 0.90,
        "confident": 0.96,
        "curious": 0.99,
        "alert": 1.02,
    }[mood]
    blended = 1.0 + (factor - 1.0) * (0.55 + 0.45 * intensity)
    return round(max(0.72, min(1.18, base * blended)), 3)


def _nano_text(text: str, reaction: str) -> tuple[str, bool]:
    """Render only paralinguistic tags documented by the upstream Nano/Turbo family."""
    tag = NANO_NATIVE_TAGS.get(reaction)
    if not tag:
        return text, False
    if reaction == "laugh":
        return f"{text} {tag}", True
    return f"{tag} {text}", True


def plan_voice(
    text: str,
    *,
    profile: str | None = None,
    mood: str | None = None,
    context: str = "chat",
    reaction: str | None = None,
    intensity: float = 0.65,
    profiles_path: Path = DEFAULT_PROFILES_PATH,
) -> dict[str, Any]:
    """Build a provider-independent Human Voice Soul V2 execution plan."""
    clean = sanitize_spoken_text(text)
    if not clean:
        raise ValueError("spoken text is empty after sanitization")
    if context not in CONTEXTS:
        context = "chat"
    resolved_mood = mood if mood in MOODS else infer_mood(clean, context)
    profiles = load_profiles(profiles_path)
    profile_id = choose_profile(profiles, profile, resolved_mood, context)
    identity = profiles["profiles"][profile_id]
    resolved_reaction = _reaction_for(resolved_mood, reaction)
    nano_text, nano_native = _nano_text(clean, resolved_reaction)

    # Normal human conversation prioritizes the light multi-voice engine.
    # Native reaction requests prefer Nano only when the runtime can preserve identity.
    engine_order = ["nano", "kokoro", "piper"] if nano_native else ["kokoro", "nano", "piper"]

    return {
        "schema": "dragon.voice-soul.v2",
        "profile": profile_id,
        "display_name": identity["display_name"],
        "persona": identity["persona"],
        "mood": resolved_mood,
        "context": context,
        "reaction": resolved_reaction,
        "intensity": round(max(0.0, min(1.0, intensity)), 3),
        "spoken_text": clean,
        "engine_order": engine_order,
        "kokoro": {
            "voice": identity["kokoro_voice"],
            "speed": _speed_for(float(identity["kokoro_speed"]), resolved_mood, intensity),
        },
        "nano": {
            "text": nano_text,
            "native_reaction_tag": nano_native,
            "reference_file": identity["reference_file"],
        },
        "piper": {"profile": identity["piper_profile"]},
        "truth": {
            "paid_api_required": False,
            "v3d_tts_inference_claimed": False,
            "exact_real_person_voice_claimed": False,
        },
    }
