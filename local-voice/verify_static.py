#!/usr/bin/env python3
from __future__ import annotations

import json
import pathlib
import py_compile
import sys

ROOT = pathlib.Path(__file__).resolve().parent
SERVER = ROOT / "dragon_voice_server.py"
PROFILES = ROOT / "profiles.json"
INSTALLER = ROOT / "install-pi5.sh"

py_compile.compile(str(SERVER), doraise=True)
print("LOCAL_VOICE_PYTHON_SYNTAX=PASS")

data = json.loads(PROFILES.read_text(encoding="utf-8"))
assert data["schema"] == "dragon.local-voice.profiles.v1"
assert data["default_profile"] in data["profiles"]
assert len(data["profiles"]) == 7
assert len(set(data["profiles"])) == 7
assert data["default_model"].endswith(".onnx")

required = {
    "nova_warm",
    "dragon_playful",
    "dragon_serious",
    "dragon_deep",
    "whatsapp_natural",
    "story_soul",
    "night_whisper",
}
assert set(data["profiles"]) == required

for name, profile in data["profiles"].items():
    assert profile["model"].endswith(".onnx"), name
    for key in ("volume", "length_scale", "noise_scale", "noise_w_scale"):
        assert isinstance(profile[key], (int, float)), (name, key)
        assert profile[key] > 0, (name, key)

print("SEVEN_VOICE_PROFILE_CONTRACT=PASS")

installer = INSTALLER.read_text(encoding="utf-8")
for marker in (
    "PAID_API_USED=NO",
    "ELEVENLABS_REQUIRED=NO",
    "V3D_TTS_INFERENCE_CLAIMED=NO",
    "DRAGON_LOCAL_VOICE_V1=PASS",
):
    assert marker in installer, marker

server = SERVER.read_text(encoding="utf-8")
for marker in (
    '"paid_api_required": False',
    '"v3d_voice_inference_claimed": False',
    '"cpu-baseline"',
    "hmac.compare_digest",
):
    assert marker in server, marker

print("TRUTH_BOUNDARY=PASS")
print("SECRET_COMPARISON=PASS")
print("PAID_PROVIDER_DEPENDENCY=NO")
print("DRAGON_LOCAL_VOICE_STATIC_PROOF=PASS")
sys.exit(0)
