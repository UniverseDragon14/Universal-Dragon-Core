#!/usr/bin/env python3
"""WhatsApp Live Voice Response Engine (orchestrator).

Pipeline per incoming voice note:
    ogg/opus  --ffmpeg-->  16kHz mono wav  --STT-->  text
    text (+history)  --LLM-->  reply text
    reply text  --TTS-->  wav  --ffmpeg-->  ogg/opus  ==> outbox

The Node bridge (bridge/index.js) owns the WhatsApp socket. It writes inbound
jobs into spool/whatsapp/inbox and sends whatever appears in spool/whatsapp/outbox.
This process never touches the network directly, which keeps the trust boundary
small and lets the engine run as an unprivileged local worker.

NOTE ON SCOPE: Baileys exposes voice *messages* (PTT), not live call audio.
WhatsApp calls are end-to-end-encrypted WebRTC and are not accessible to a
userland bot. This engine therefore targets voice notes — near-real-time,
which is what a chat assistant actually needs.

Run:
    python -m carryon.whatsapp_voice.engine
"""
from __future__ import annotations

import json
import os
import subprocess
import time
import uuid
from collections import defaultdict, deque

from carryon.common.log import get_logger
from carryon.whatsapp_voice import llm_client, stt, tts

MARKER = "CARRYON_WA_ENGINE_V01"
VERSION = "0.1.0"

log = get_logger("wa.engine")

SPOOL = os.environ.get("CARRYON_SPOOL", os.path.join(os.path.dirname(__file__), "..", "spool", "whatsapp"))
INBOX = os.path.abspath(os.path.join(SPOOL, "inbox"))
OUTBOX = os.path.abspath(os.path.join(SPOOL, "outbox"))
WORK = os.path.abspath(os.path.join(SPOOL, "work"))
POLL_SECONDS = float(os.environ.get("CARRYON_POLL_SECONDS", "1.0"))

# Small rolling memory keyed by chat id; deque bounds RAM on a Pi/phone.
_history: dict[str, deque] = defaultdict(lambda: deque(maxlen=6))


def _ffmpeg(args: list[str]) -> None:
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *args]
    subprocess.run(cmd, check=True)


def _to_wav(src_audio: str, out_wav: str) -> None:
    # WhatsApp PTT is opus in ogg; normalise to 16kHz mono for STT.
    _ffmpeg(["-i", src_audio, "-ar", "16000", "-ac", "1", out_wav])


def _to_ptt(src_wav: str, out_ogg: str) -> None:
    # libopus in ogg is what WhatsApp expects for a playable voice note.
    _ffmpeg(["-i", src_wav, "-c:a", "libopus", "-b:a", "32k", "-ar", "48000", "-ac", "1", out_ogg])


def _process(job_path: str) -> None:
    with open(job_path, "r", encoding="utf-8") as fh:
        job = json.load(fh)

    chat_id = job.get("chat_id", "unknown")
    audio_in = job["audio_path"]
    job_id = job.get("id", uuid.uuid4().hex)
    log.info("job received", id=job_id, chat=chat_id, audio=audio_in)

    os.makedirs(WORK, exist_ok=True)
    wav_in = os.path.join(WORK, f"{job_id}.in.wav")
    wav_out = os.path.join(WORK, f"{job_id}.out.wav")
    ogg_out = os.path.join(OUTBOX, f"{job_id}.reply.ogg")

    _to_wav(audio_in, wav_in)
    utterance = stt.transcribe(wav_in)
    log.info("transcribed", id=job_id, text=utterance)

    history = list(_history[chat_id])
    answer = llm_client.reply(utterance, history)
    log.info("reply generated", id=job_id, text=answer)

    _history[chat_id].append({"role": "user", "text": utterance})
    _history[chat_id].append({"role": "model", "text": answer})

    tts.synthesize(answer, wav_out)
    _to_ptt(wav_out, ogg_out)

    out_job = {
        "id": job_id,
        "chat_id": chat_id,
        "reply_text": answer,
        "reply_audio": ogg_out,
        "reply_to": job.get("message_id"),
        "kind": "voice",
        "ts": time.time(),
    }
    tmp = ogg_out + ".job.json.tmp"
    final = os.path.join(OUTBOX, f"{job_id}.job.json")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(out_job, fh, ensure_ascii=False)
    os.replace(tmp, final)  # atomic publish so the bridge never reads a half file
    log.info("reply published", id=job_id, out=final)

    for path in (wav_in, wav_out):
        try:
            os.remove(path)
        except OSError:
            pass


def main() -> None:
    for d in (INBOX, OUTBOX, WORK):
        os.makedirs(d, exist_ok=True)
    log.info("engine online", inbox=INBOX, outbox=OUTBOX,
             stt=os.environ.get("CARRYON_STT_BACKEND", "stub"),
             tts=os.environ.get("CARRYON_TTS_BACKEND", "stub"),
             llm=os.environ.get("CARRYON_LLM_BACKEND", "echo"))
    while True:
        jobs = sorted(f for f in os.listdir(INBOX) if f.endswith(".job.json"))
        for name in jobs:
            job_path = os.path.join(INBOX, name)
            try:
                _process(job_path)
            except Exception as exc:
                log.error("job failed", job=name, error=str(exc))
            finally:
                try:
                    os.remove(job_path)
                except OSError:
                    pass
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
