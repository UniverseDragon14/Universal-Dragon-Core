# Dragon Room Magic V1 Validation Evidence

Feature branch: `feat/dragon-room-magic-voice-soul-v1`

Tracked by: issue #23 and PR #24.

## Proven in GitHub Actions

The dedicated `Dragon Room Magic V1` workflow validates the pull-request merge candidate, not just an isolated source file.

Required gates:

- TypeScript compile check
- deterministic Voice Soul contract proof
- production Vite build
- portable Termux HTML and shell syntax checks
- empty secret-placeholder verification
- protected server voice-gate markers
- isolated Termux handoff installer replay

The deterministic Voice Soul proof emits:

```text
VOICE_SOUL_SCHEMA=PASS
VOICE_SOUL_SANITIZER=PASS
VOICE_SOUL_TRUNCATED_REASONING=PASS
VOICE_SOUL_TAG_INJECTION=PASS
VOICE_SOUL_MOOD_BOUNDARIES=PASS
VOICE_SOUL_CONTEXT_PRIORITY=PASS
VOICE_SOUL_ROOM_CUES=PASS
ELEVEN_V3_RENDERER=PASS
DRAGON_VOICE_SOUL_V1=PASS
```

The portable handoff proof emits:

```text
TERMUX_PORTABLE_ASSETS=PASS
SECRET_FILES_TOUCHED=NO
ROOM_MAGIC_HANDOFF_INSTALL=PASS
TERMUX_HANDOFF_PROOF=PASS
```

## Repository-wide regression signal

On the same feature head, the existing NOVA/QBIT workflows also remain green:

- NOVA QBIT Tests
- QBIT NOVA CI and SEO
- QBIT NOVA v0.8 Native Engine
- QBIT NOVA v0.9 Token Pipeline
- QBIT NOVA v1.0 CLI Native
- QBIT NOVA v1.1 Portable Launcher
- QBIT NOVA v1.2 Installer
- QBIT NOVA v1.3 Release Bundle

## Not yet claimed as proven

These require the real device/account and are deliberately not replaced by CI simulation:

- Huawei Termux replay of the new V3 handoff
- exact Arabella ElevenLabs voice ID
- one real Eleven v3 Arabella generation with laugh/breath/whisper quality verification
- Pi5 Dragon Brain integration while the Pi5 origin is unreachable
- Pico hardware integration
- hologram-fan proprietary BIN conversion or wireless upload

## Known technical debt observed during validation

`npm ci` currently reports dependency vulnerabilities in the existing dependency tree, and Vite reports a large main JavaScript chunk after minification. These warnings are not silently auto-fixed in this feature PR because dependency upgrades and bundle restructuring require a separate controlled audit and regression pass.
