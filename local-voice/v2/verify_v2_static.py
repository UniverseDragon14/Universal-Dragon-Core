from __future__ import annotations

import json
from pathlib import Path

from voice_soul_v2 import plan_voice, sanitize_spoken_text

ROOT = Path(__file__).resolve().parent


def require(condition: bool, marker: str) -> None:
    """Fail the proof immediately when a required contract is false."""
    if not condition:
        raise SystemExit(f"{marker}=FAIL")
    print(f"{marker}=PASS")


for filename in ("voice_soul_v2.py", "dragon_voice_v2_server.py"):
    source = (ROOT / filename).read_text(encoding="utf-8")
    compile(source, str(ROOT / filename), "exec")
print("HUMAN_VOICE_V2_PYTHON_SYNTAX=PASS")

profiles = json.loads((ROOT / "profiles-v2.json").read_text(encoding="utf-8"))
expected = {
    "nova_warm",
    "dragon_playful",
    "dragon_serious",
    "dragon_deep",
    "whatsapp_natural",
    "story_soul",
    "night_whisper",
}
require(set(profiles["profiles"]) == expected, "SEVEN_HUMAN_VOICE_IDENTITIES")

clean = sanitize_spoken_text("Hello <analysis>private thought</analysis> [laugh] human")
require("private thought" not in clean and "[laugh]" not in clean and clean == "Hello human", "VOICE_SOUL_V2_SANITIZER")

whatsapp = plan_voice("Bro, I will reply now.", context="whatsapp")
require(whatsapp["profile"] == "whatsapp_natural", "WHATSAPP_NATURAL_ROUTING")

laugh = plan_voice("That is hilarious haha", mood="laugh", context="chat")
require(laugh["profile"] == "dragon_playful", "PLAYFUL_LAUGH_ROUTING")
require(laugh["nano"]["native_reaction_tag"] is True and "[laugh]" in laugh["nano"]["text"], "NANO_NATIVE_LAUGH_PLAN")

serious = plan_voice("Critical warning. Stop now.", context="alert")
require(serious["profile"] == "dragon_serious", "SERIOUS_ALERT_ROUTING")

deep = plan_voice("Systems online.", context="robot")
require(deep["profile"] == "dragon_deep", "ROBOT_DEEP_ROUTING")

night = plan_voice("Speak softly tonight.", context="night")
require(night["profile"] == "night_whisper", "WHISPER_ROUTING")

truth = whatsapp["truth"]
require(truth["paid_api_required"] is False, "PAID_API_REQUIRED_NO")
require(truth["v3d_tts_inference_claimed"] is False, "V3D_TTS_CLAIM_NO")
require(truth["exact_real_person_voice_claimed"] is False, "REAL_PERSON_CLONE_CLAIM_NO")

server = (ROOT / "dragon_voice_v2_server.py").read_text(encoding="utf-8")
require("hmac.compare_digest" in server and "if not ACCESS_TOKEN:\n        return False" in server, "V2_FAIL_CLOSED_AUTH")
require("127.0.0.1:8123" in server, "PROVEN_V1_FALLBACK_WIRED")

print("HUMAN_VOICE_SOUL_V2_STATIC_PROOF=PASS")
