# Dragon Room Magic V1

This folder is the portable handoff for the Dragon Resonance vertical slice tracked in issue #23.

## What is ready

- `termux/awaken.html` — self-contained mobile Dragon Resonance visual with no external assets.
- `termux/awaken-v3.sh` — bounded Huawei Termux launcher for visual, vibration, optional local room sound, torch pulses, expressive voice, and Android TTS fallback.
- `termux/voice-eleven-v3.sh` — direct Eleven v3 Termux adapter. It reads credentials only from a local secret file and never prints them.
- `termux/install-v1.sh` — safe handoff installer. It backs up existing Room Magic files, copies the new portable set atomically, preserves secret files, syntax-checks scripts, and creates the original procedural room sound only when it is missing.
- `elevenlabs.env.example` — empty configuration template only. Real values must remain local.
- `src/voice/voiceSoul.ts` — provider-independent Voice Soul planning contract in the main app.
- `src/voice/elevenV3.ts` — Eleven v3 prompt renderer.
- `server.ts` — protected server-side `/api/voice/status` and `/api/voice/speak` integration. The billable speech endpoint is disabled unless a separate Dragon access token is configured.

## Safety boundary

V1 does not send commands to the Raspberry Pi, Pico, hologram fan, or any other remote hardware. Hologram fan upload stays disabled until its proprietary format/protocol is proven.

No API keys, access tokens, real voice IDs, auth files, or secret `.env` values belong in GitHub.

The Termux HTTP launcher serves a dedicated runtime directory containing only `awaken.html`; it does not expose the whole lab directory over loopback.

## Huawei Termux handoff

After checking out this branch on Huawei, install the tested portable files from the repository root:

```bash
bash room-magic/termux/install-v1.sh
```

Expected installer proof:

```text
SECRET_FILES_TOUCHED=NO
ROOM_MAGIC_HANDOFF_INSTALL=PASS
```

If existing Room Magic files are present, the installer backs them up under `~/.dragon-magic-backups/<UTC timestamp>/` before replacement. It does not copy or modify ElevenLabs credentials.

Then run:

```bash
"$HOME/dragon-room-magic-v1/awaken-v3.sh"
```

Without ElevenLabs credentials, the launcher still works and falls back to Android TTS.

For direct Termux expressive voice later, create this local-only file:

```text
~/.config/universal-dragon/secrets/elevenlabs.env
```

with these variable names:

```text
ELEVENLABS_API_KEY=<local secret>
ELEVENLABS_VOICE_ID=<saved Arabella voice id>
ELEVENLABS_MODEL=eleven_v3
```

Protect it with mode `600`. Never commit it.

Expected Room Magic proof markers include:

```text
HTTP_ASSET_IDENTITY=PASS
VISUAL_HTTP=PASS
VOICE_PATH=ELEVEN_V3
ROOM_EFFECTS=BOUNDED
REMOTE_HARDWARE_COMMANDS=NO
DRAGON_ROOM_MAGIC_V3=PASS
```

If the expressive provider is not configured, `VOICE_PATH=ANDROID_TTS_FALLBACK` is expected and the rest of Room Magic still runs. The local generated WAV is a separate room-effect layer, not a speech fallback.

## Protected server-side voice contract

The already-configured Pi5 `OPENAI_API_KEY` remains only in the server runtime environment. This repository, the status endpoints, and application logs never list, copy, return, or print its value.

### Provider modes

- `local` is the safe default. The protected endpoint returns a `202` client-TTS instruction and makes no paid provider request.
- `openai` enables OpenAI Text-to-Speech only when the existing runtime key is available.
- `elevenlabs` keeps the existing optional server-side ElevenLabs flow available.
- A request body cannot select a provider; only the server environment can do that.

Use `room-magic/openai.env.example` as a names-only template. Do not add real secrets to it or commit a populated `.env` file.

```text
DRAGON_VOICE_PROVIDER=local
DRAGON_VOICE_ACCESS_TOKEN=<separate strong bearer token>
OPENAI_TTS_MODEL=gpt-4o-mini-tts
DRAGON_VOICE_DEFAULT_PROFILE=NOVA
DRAGON_VOICE_MAX_INPUT_CHARS=400
DRAGON_VOICE_DAILY_MAX_REQUESTS=6
DRAGON_VOICE_DAILY_MAX_CHARACTERS=2400
DRAGON_VOICE_USAGE_FILE=<optional local path>
```

When `DRAGON_VOICE_PROVIDER=openai`, the existing `OPENAI_API_KEY` must already be loaded by the service environment. It is intentionally not duplicated in this template.

### Six built-in voice profiles

| Profile | OpenAI built-in voice | Intended style |
| --- | --- | --- |
| `NOVA` | `marin` | warm, clear assistant |
| `EVE` | `cedar` | friendly and confident |
| `DRAGON` | `onyx` | deliberate and protective |
| `ANANYA` | `coral` | bright and gentle |
| `GUARDIAN` | `sage` | calm safety guidance |
| `NARRATOR` | `alloy` | balanced storytelling |

These are built-in provider voices only. This implementation does not train, clone, or upload anyone's voice.

### Calling the protected endpoint

`POST /api/voice/speak` always requires:

```text
Authorization: Bearer <DRAGON_VOICE_ACCESS_TOKEN>
```

A paid provider additionally requires a strict per-request opt-in:

```json
{
  "text": "Heey, Aslam... Dragon Resonance is active.",
  "mood": "PLAYFUL",
  "context": "WAKE",
  "voice_profile": "NOVA",
  "premium": true
}
```

With `local`, the response is a `202` JSON instruction containing sanitized text for client-side/Android TTS. With `openai` or `elevenlabs`, omitting `"premium": true` returns `premium_voice_opt_in_required` and no billable request is made.

Successful paid audio is MP3 and includes `X-Dragon-AI-Generated: true`. The playback UI must clearly disclose that the voice is AI-generated before the user hears it.

### Cost and safety guard

- The default limit is 400 input characters, 6 paid requests/day, and 2,400 paid characters/day.
- Usage resets on the UTC date and is written to `data/dragon-voice-usage.json`, which is ignored by Git.
- A paid request reserves its budget before contacting a provider. Provider failures are not rolled back, which intentionally favors cost safety.
- Corrupt or unavailable usage-state storage fails closed with `voice_budget_state_unavailable`; it does not make a paid fallback request.
- The JSON state file is designed for the single Pi5 service process. A future multi-instance deployment needs a shared atomic usage store.
- Private reasoning tags and bracketed audio labels are removed by the Voice Soul planner before text is returned or sent to a provider.

The existing ElevenLabs secret variables remain supported for the `elevenlabs` provider:

```text
ELEVENLABS_API_KEY=<server secret>
ELEVENLABS_VOICE_ID=<saved provider voice id>
ELEVENLABS_MODEL=eleven_v3
```

The provider key, bearer token, and voice ID are never returned by `/api/voice/status` or `/api/health`.
## Next integration gates

1. Keep CI and automated review clean.
2. Save the exact Arabella voice in the ElevenLabs account and set its ID only in the local secret store.
3. Restore Pi5 connectivity and connect the existing Dragon brain reply to the Voice Soul contract.
4. Add Pico/device event adapters only after explicit hardware mapping.
5. Integrate HoloCore only after fan BIN/protocol proof.
