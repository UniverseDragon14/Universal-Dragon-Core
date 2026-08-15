# Universal Dragon Local Voice V1

## Goal

Run speech generation on the Raspberry Pi 5 without ElevenLabs or another paid speech API, while preserving the existing provider-independent Dragon Voice Soul planner.

## V1 architecture

```text
NOVA / EVE / WhatsApp reply
        |
        v
Dragon Voice Soul planner
        |
        v
Dragon Local Voice API :8123
        |
        v
Piper / ONNX Runtime
        |
        v
WAV audio
```

The local service binds to `127.0.0.1` by default and is intended to be exposed only through an authenticated local adapter or a separately configured Cloudflare tunnel.

## Seven voice-profile slots

V1 defines seven stable identities:

- `nova_warm`
- `dragon_playful`
- `dragon_serious`
- `dragon_deep`
- `whatsapp_natural`
- `story_soul`
- `night_whisper`

A profile is not falsely claimed to be a distinct trained speaker until its dedicated ONNX model exists. Missing dedicated models fall back to the bootstrap model and the HTTP response exposes `X-Dragon-Model-Fallback: yes`.

## Truth boundary

- No OpenAI API key required for speech generation.
- No ElevenLabs key required.
- No paid speech provider required.
- Pi5 V3D GPU inference is **not** claimed in V1.
- The already-proven V3D/Vulkan work is a separate accelerator path. Piper uses ONNX Runtime; CUDA flags from upstream do not turn Raspberry Pi V3D into CUDA.
- V1 establishes a truthful local CPU baseline first. A later measured accelerator stage may add custom V3D kernels only where evidence shows a real benefit.

## Pi5 install

From a checkout of this branch:

```bash
bash local-voice/install-pi5.sh
```

Expected final markers:

```text
SYSTEM_DEPENDENCIES=PASS
PYTHON_ENV=PASS
BOOTSTRAP_MODEL=PASS
LOCAL_SECRET_FILE=PASS
SERVICE_INSTALL=PASS
LOCAL_VOICE_HEALTH=PASS
LOCAL_WAV_GENERATION=PASS
PAID_API_USED=NO
ELEVENLABS_REQUIRED=NO
V3D_TTS_INFERENCE_CLAIMED=NO
DRAGON_LOCAL_VOICE_V1=PASS
```

The generated proof audio is stored at:

```text
~/dragon-local-voice-v1/proof.wav
```

## API

Health:

```bash
curl http://127.0.0.1:8123/health
```

Synthesis:

```bash
source ~/dragon-local-voice-v1/.env
curl -H "Authorization: Bearer $DRAGON_VOICE_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"text":"Hi Aslam, NOVA is online.","profile":"whatsapp_natural","intensity":0.65}' \
  http://127.0.0.1:8123/v1/speak \
  -o reply.wav
```

## Huawei / Termux handoff

`room-magic/termux/voice-local-pi5.sh` is a small client. Point it at the protected Pi endpoint with local-only environment variables and it downloads a WAV voice reply.

## Voice model policy

Model weights are never committed automatically. Put trained or licensed ONNX files in the Pi model directory. Each third-party voice model has its own license, so its model card must be reviewed before commercial distribution.

The bootstrap engine is Piper from the Open Home Foundation. Piper supports arm64 and custom voice training, but Piper itself is GPL-3.0-or-later. Keep the engine isolated behind this service boundary and perform a license review before shipping a closed-source commercial appliance.

## Quality roadmap

V1 is the reliable offline speech floor, not a claim that one bootstrap voice already beats ElevenLabs. The path to that target is:

1. establish Pi5 latency and audio-quality baseline;
2. collect or license clean training audio for owned Dragon voices;
3. train/fine-tune dedicated models for the seven profile slots;
4. measure naturalness, speaker consistency, Tamil/Tanglish pronunciation and latency;
5. add expressive breath/laugh/pacing controls in the Voice Soul planner;
6. benchmark any V3D acceleration separately and fail closed on CPU fallback when a GPU claim is made.
