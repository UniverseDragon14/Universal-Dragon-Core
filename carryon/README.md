# Carry-On — Automation & Intelligence Core

A modular local core for **Universal Dragon** that bridges local hardware with
generative AI agents. Built for **ARM64 / Termux / Linux** (Pi5, phone, or server).

Three modules, one design rule: **every module logs to `stderr` only** so
`stdout` stays a clean JSON-RPC channel for MCP stdio transports.

```
carryon/
├── common/log.py            # stderr-only structured logger (MCP-safe)
├── whatsapp_voice/          # 1. WhatsApp voice-note -> STT -> LLM -> TTS
│   ├── engine.py            #    Python orchestrator (spool worker)
│   ├── stt.py tts.py llm_client.py
│   └── bridge/index.js      #    Node/Baileys WhatsApp socket <-> spool
├── media_pipeline/          # 2. FFmpeg + OpenCV photo/video editing
│   ├── ffmpeg_ops.py opencv_ops.py cli.py
├── carryon_gateway/         # 3. Authenticated local command gateway
│   ├── server.py client.py actions.py guard.py
├── bin/                     #    operator-provided shield/subagent scripts
├── scripts/                 #    run_whatsapp.sh  run_gateway.sh
└── spool/whatsapp/{inbox,outbox}
```

## Install

```bash
# System deps (Termux shown; use apt on Debian/Pi OS)
pkg install python nodejs ffmpeg espeak         # apt install python3 nodejs ffmpeg espeak-ng

# Python: nothing required for stub/echo mode. Install per-backend as needed:
pip install faster-whisper piper-tts opencv-python-headless numpy   # optional

# Node bridge deps
cd carryon/whatsapp_voice/bridge && npm install && cd -

cp carryon/.env.example .env        # then edit .env
```

Everything boots with **zero optional deps** using the `stub`/`echo` backends,
so you can wire and test the whole flow before installing models.

---

## 1. WhatsApp Voice Response Engine

**Flow:** incoming voice note → `ffmpeg` → 16 kHz wav → **STT** → text →
(+chat memory) **LLM** → reply → **TTS** → wav → `ffmpeg` → opus/ogg → sent back.

The Node **bridge** owns the WhatsApp socket (Baileys) and the Python **engine**
does the AI work. They talk through a file **spool** (`inbox`/`outbox`) with
atomic renames, so a crash in one never corrupts the other and neither needs the
other's dependencies.

```bash
./carryon/scripts/run_whatsapp.sh          # starts engine + bridge; scan the QR once
```

Backends are swappable by env var:

| Stage | env | options |
|-------|-----|---------|
| STT | `CARRYON_STT_BACKEND` | `whisper_cpp` · `faster_whisper` · `stub` |
| LLM | `CARRYON_LLM_BACKEND` | `gemini` · `http` (Ollama) · `echo` |
| TTS | `CARRYON_TTS_BACKEND` | `piper` · `espeak` · `stub` |

> **Scope note (honest):** Baileys delivers voice **messages** (PTT), not live
> **call** audio. WhatsApp calls are E2E-encrypted WebRTC and are not accessible
> to a userland client — no library can tap them. This engine targets voice
> notes, which is what a chat assistant actually uses, and responds near-real-time.

---

## 2. Media Pipeline (FFmpeg + OpenCV)

Auditable wrappers — explicit argument lists, no shell string interpolation, so
paths can't inject flags.

```bash
python -m carryon.media_pipeline.cli probe        in.mp4
python -m carryon.media_pipeline.cli slice        in.mp4 out.mp4 --start 5 --duration 10
python -m carryon.media_pipeline.cli scale        in.mp4 out.mp4 --width 1280
python -m carryon.media_pipeline.cli denoise      in.mp4 out.mp4         # hqdn3d + afftdn
python -m carryon.media_pipeline.cli contrast     in.mp4 out.mp4         # ffmpeg static eq
python -m carryon.media_pipeline.cli autocontrast in.mp4 out.mp4         # OpenCV CLAHE, per-frame
```

`autocontrast` is the **dynamic frame-contrast correction** — adaptive CLAHE on
the LAB L-channel, handling clips whose lighting changes shot to shot (ffmpeg's
`eq` is a static curve by comparison).

---

## 3. Carry-On Command Gateway

A **local, authenticated** control plane — deliberately *not* a hidden backdoor.
Obscurity is used nowhere; security comes from layers you can audit:

1. **Transport** — Unix socket, `0600` (owner-only). No network exposure by
   default. Optional TCP is **loopback-only and enforced** (non-loopback binds
   are refused).
2. **Authenticity** — every request is HMAC-SHA256 signed over its canonical
   bytes with a shared secret. Bad signature → nothing runs.
3. **Freshness** — a unix `ts` (±window) and a one-time `nonce` block replay of
   captured requests.
4. **Authorization** — the action must be in a fixed **allowlist** *and* pass
   **Nova Guard**. `blocked` → refused; `needs_approval` → refused unless the
   request is signed with `approval=true`. It reuses the repo's
   `tools/qbit_nova_guard_approval_v06.py`, so the gateway shares one policy with
   the rest of QBIT NOVA (with a conservative built-in fallback).

The gateway **never runs arbitrary shell.** It exposes named actions
(`ping`, `status`, `nova_guard_shield`, `launch_subagent`, `media`); shields and
sub-agents resolve only to scripts inside `carryon/bin/` (path-traversal blocked).

```bash
# generate a strong secret once
export CARRYON_GATEWAY_SECRET="$(head -c 32 /dev/urandom | base64)"

./carryon/scripts/run_gateway.sh           # server

# in another shell (same secret):
python -m carryon.carryon_gateway.client ping
python -m carryon.carryon_gateway.client status
python -m carryon.carryon_gateway.client nova_guard_shield --param shield=firewall --approve
python -m carryon.carryon_gateway.client launch_subagent --param name=example --approve
python -m carryon.carryon_gateway.client media --param 'argv=["probe","in.mp4"]'
```

Add capability by adding an entry to `actions.py` and a script to `bin/` — on
purpose, reviewably — never by passing a command string over the wire.

---

## Deploy on Termux (background, survives app close)

```bash
# keep the gateway alive like you did with cloudflared
nohup ./carryon/scripts/run_gateway.sh > ~/carryon-gw.log 2>&1 &
disown
nohup ./carryon/scripts/run_whatsapp.sh > ~/carryon-wa.log 2>&1 &
disown
```

On a Pi5, prefer `systemd` units (one per module) with `Restart=on-failure` and
`EnvironmentFile=` pointing at your `.env`.
