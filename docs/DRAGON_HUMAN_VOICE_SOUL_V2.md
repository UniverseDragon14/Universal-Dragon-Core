# Dragon Human Voice Soul V2

Human Voice Soul V2 is the local expressive layer above the already-proven Pi5 Piper V1 service.

## Goal

One local voice service for NOVA, EVE, Novakutty, Room Magic, WhatsApp voice replies, phone clients, and future robot/device adapters.

The target is human-like variation, not a single generic TTS voice. The system separates **identity**, **mood**, **context**, **reaction**, and **engine** so the assistant can change delivery without changing its safety or truth boundary.

## Seven identities

- `nova_warm` — warm everyday assistant
- `dragon_playful` — smiling/playful energy
- `dragon_serious` — firm controlled delivery
- `dragon_deep` — mature cinematic authority
- `whatsapp_natural` — casual short voice-note delivery
- `story_soul` — measured storyteller
- `night_whisper` — soft late-night presence

These are original Dragon identity slots. They are not claims of an exact real actor or public figure voice.

## Mood and reaction controls

Planner moods:

`neutral`, `smile`, `laugh`, `serious`, `whisper`, `sad`, `confident`, `curious`, `alert`

Contexts:

`chat`, `whatsapp`, `wake`, `story`, `robot`, `alert`, `night`

Reaction routing includes bounded plans for laugh/chuckle/cough and non-native fallbacks such as sigh/breath. Only upstream-confirmed Chatterbox reaction tags are emitted directly by the Nano lane.

## Engine order

1. **Kokoro** — primary lightweight multi-identity natural speech lane.
2. **Chatterbox Nano** — optional expressive/paralinguistic lane. A local permissioned reference WAV is required by default when identity preservation matters.
3. **Piper V1** — already-proven fail-safe local fallback.

The router can be forced to a single engine for testing, or set to `auto` for fallback behavior.

## Security boundary

- local bearer token is required; missing token fails closed
- token remains in the existing Pi5 V1 `.env` and is not committed
- reference WAV files remain local and are not committed
- model paths/reference paths reject traversal
- speech text is bounded to 1200 characters
- private-reasoning markup and arbitrary bracketed audio-tag injection are removed before planning
- services bind to loopback by default

## Truth boundary

- paid API required: **no**
- ElevenLabs required: **no**
- Pi5 V3D TTS inference claimed: **no**
- exact real-person voice cloning claimed: **no**
- V1 Piper runtime proof: **complete on real Pi5**
- V2 Kokoro runtime proof on Pi5: **required before V2 merge**
- Chatterbox Nano runtime/audio benchmark on Pi5: **required before claiming practical real-time performance**

## Pi5 files

- `local-voice/v2/voice_soul_v2.py` — provider-independent planner
- `local-voice/v2/dragon_voice_v2_server.py` — V2 API/router
- `local-voice/v2/profiles-v2.json` — seven identities
- `local-voice/v2/install-v2-pi5.sh` — Kokoro V2 install/proof
- `local-voice/v2/install-nano-pi5.sh` — optional Nano install
- `local-voice/v2/proof-seven-voices.sh` — generate seven local identity proofs
- `room-magic/termux/voice-local-pi5-v2.sh` — Huawei/Termux client

## API

Local default: `http://127.0.0.1:8124`

- `GET /health`
- `GET /v2/profiles` — authenticated
- `POST /v2/plan` — authenticated
- `POST /v2/speak` — authenticated

Example request body:

```json
{
  "text": "Bro, I am here.",
  "profile": "whatsapp_natural",
  "mood": "smile",
  "context": "whatsapp",
  "reaction": "none",
  "engine": "auto",
  "intensity": 0.68
}
```

## Voice references

Any reference WAV used by the Nano lane must be a voice the project owner has permission to use. Reference files stay under the local V2 `references/` directory and are deliberately excluded from Git and CI artifacts.
