# Dragon Room Magic V1

This folder is the portable handoff for the Dragon Resonance vertical slice tracked in issue #23.

## What is ready

- `termux/awaken.html` — self-contained mobile Dragon Resonance visual with no external assets.
- `termux/awaken-v3.sh` — bounded Huawei Termux launcher for visual, vibration, optional local sound, torch pulses, and Android TTS fallback.
- `src/voice/voiceSoul.ts` — provider-independent Voice Soul planning contract in the main app.
- `src/voice/elevenV3.ts` — prompt renderer for Eleven v3. It does not store credentials or call the provider.

## Safety boundary

V1 does not send commands to the Raspberry Pi, Pico, hologram fan, or any other remote hardware. Hologram fan upload stays disabled until its proprietary format/protocol is proven.

No API keys, access tokens, voice IDs, auth files, or `.env` values belong in GitHub.

## Huawei Termux handoff

When the device is available, copy the two portable files into the existing lab directory:

```bash
mkdir -p "$HOME/dragon-room-magic-v1"
cp awaken.html "$HOME/dragon-room-magic-v1/awaken.html"
cp awaken-v3.sh "$HOME/dragon-room-magic-v1/awaken-v3.sh"
chmod 700 "$HOME/dragon-room-magic-v1/awaken-v3.sh"
```

Then run:

```bash
"$HOME/dragon-room-magic-v1/awaken-v3.sh"
```

Expected proof markers include:

```text
VISUAL_HTTP=PASS
ROOM_EFFECTS=BOUNDED
REMOTE_HARDWARE_COMMANDS=NO
DRAGON_ROOM_MAGIC_V3=PASS
```

## Next integration gates

1. Review and merge this vertical slice only after CI and code review are clean.
2. Add server-side expressive-voice provider adapter without committing credentials.
3. Restore Pi5 connectivity and connect the existing Dragon brain output to the Voice Soul contract.
4. Add Pico/device event adapters only after explicit hardware mapping.
5. Integrate HoloCore only after fan BIN/protocol proof.
