# Dragon Room Magic V1

This folder is the portable handoff for the Dragon Resonance vertical slice tracked in issue #23.

## What is ready

- `termux/awaken.html` — self-contained mobile Dragon Resonance visual with no external assets.
- `termux/awaken-v3.sh` — bounded Huawei Termux launcher for visual, vibration, optional local room sound, torch pulses, expressive voice, and Android TTS fallback.
- `termux/voice-eleven-v3.sh` — direct Eleven v3 Termux adapter. It reads credentials only from a local secret file and never prints them.
- `elevenlabs.env.example` — empty configuration template only. Real values must remain local.
- `src/voice/voiceSoul.ts` — provider-independent Voice Soul planning contract in the main app.
- `src/voice/elevenV3.ts` — Eleven v3 prompt renderer.
- `server.ts` — server-side `/api/voice/status` and `/api/voice/speak` integration using `ELEVENLABS_API_KEY` and `ELEVENLABS_VOICE_ID` from the runtime environment.

## Safety boundary

V1 does not send commands to the Raspberry Pi, Pico, hologram fan, or any other remote hardware. Hologram fan upload stays disabled until its proprietary format/protocol is proven.

No API keys, access tokens, real voice IDs, auth files, or secret `.env` values belong in GitHub.

The Termux HTTP launcher serves a dedicated runtime directory containing only `awaken.html`; it does not expose the whole lab directory over loopback.

## Huawei Termux handoff

After cloning or downloading this repository, run the copy commands from the repository root:

```bash
cd room-magic/termux
mkdir -p "$HOME/dragon-room-magic-v1"
cp awaken.html "$HOME/dragon-room-magic-v1/awaken.html"
cp awaken-v3.sh "$HOME/dragon-room-magic-v1/awaken-v3.sh"
cp voice-eleven-v3.sh "$HOME/dragon-room-magic-v1/voice-eleven-v3.sh"
chmod 700 \
  "$HOME/dragon-room-magic-v1/awaken-v3.sh" \
  "$HOME/dragon-room-magic-v1/voice-eleven-v3.sh"
```

Without ElevenLabs credentials, the launcher still works and falls back to Android TTS.

For expressive voice later, create this local-only file:

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

Then run:

```bash
"$HOME/dragon-room-magic-v1/awaken-v3.sh"
```

Expected proof markers include:

```text
HTTP_ASSET_IDENTITY=PASS
VISUAL_HTTP=PASS
VOICE_PATH=ELEVEN_V3
ROOM_EFFECTS=BOUNDED
REMOTE_HARDWARE_COMMANDS=NO
DRAGON_ROOM_MAGIC_V3=PASS
```

If the expressive provider is not configured, `VOICE_PATH=ANDROID_TTS_FALLBACK` is expected and the rest of Room Magic still runs. The local generated WAV is a separate room-effect layer, not a speech fallback.

## Server-side voice contract

`POST /api/voice/speak`

```json
{
  "text": "Heey, Aslam... Dragon Resonance is active.",
  "mood": "PLAYFUL",
  "context": "WAKE"
}
```

The server converts the provider-neutral Voice Soul plan into Eleven v3 prompt text and returns MP3 audio. The voice ID is never returned by `/api/voice/status` or `/api/health`.

## Next integration gates

1. Keep CI and automated review clean.
2. Save the exact Arabella voice in the ElevenLabs account and set its ID only in the local secret store.
3. Restore Pi5 connectivity and connect the existing Dragon brain reply to the Voice Soul contract.
4. Add Pico/device event adapters only after explicit hardware mapping.
5. Integrate HoloCore only after fan BIN/protocol proof.
