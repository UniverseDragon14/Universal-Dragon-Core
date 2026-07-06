#!/usr/bin/env python3
"""FFmpeg-backed media operations.

Thin, auditable wrappers around ffmpeg/ffprobe. Every function builds an
explicit argument list (no shell string interpolation) so user-supplied paths
can never inject flags or shell metacharacters. All ffmpeg chatter is dropped;
our own structured logs go to stderr via carryon.common.log.
"""
from __future__ import annotations

import json
import shutil
import subprocess

from carryon.common.log import get_logger

MARKER = "CARRYON_MEDIA_FFMPEG_V01"
VERSION = "0.1.0"

log = get_logger("media.ffmpeg")


def _require(binary: str) -> str:
    path = shutil.which(binary)
    if not path:
        raise RuntimeError(f"{binary} not found on PATH")
    return path


def _run(args: list[str]) -> None:
    cmd = [_require("ffmpeg"), "-y", "-hide_banner", "-loglevel", "error", *args]
    log.info("ffmpeg", args=args)
    subprocess.run(cmd, check=True)


def probe(src: str) -> dict:
    """Return width/height/duration/fps for a media file."""
    cmd = [
        _require("ffprobe"), "-v", "error", "-print_format", "json",
        "-show_streams", "-show_format", src,
    ]
    out = subprocess.run(cmd, check=True, capture_output=True, text=True).stdout
    data = json.loads(out)
    v = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), {})
    num, den = (v.get("avg_frame_rate", "0/1").split("/") + ["1"])[:2]
    fps = (float(num) / float(den)) if float(den or 1) else 0.0
    return {
        "width": v.get("width"),
        "height": v.get("height"),
        "duration": float(data.get("format", {}).get("duration", 0.0)),
        "fps": round(fps, 3),
    }


def slice_clip(src: str, dst: str, start: float, duration: float) -> str:
    """Cut a segment. Uses stream copy for a fast, lossless slice."""
    _run(["-ss", str(start), "-i", src, "-t", str(duration), "-c", "copy", dst])
    return dst


def scale(src: str, dst: str, width: int, height: int = -2) -> str:
    """Resolution scaling. height=-2 preserves aspect ratio (even dimension)."""
    _run(["-i", src, "-vf", f"scale={int(width)}:{int(height)}", dst])
    return dst


def denoise(src: str, dst: str) -> str:
    """Noise filtering: hqdn3d for video, afftdn for audio."""
    _run(["-i", src, "-vf", "hqdn3d=1.5:1.5:6:6", "-af", "afftdn=nr=12", dst])
    return dst


def contrast(src: str, dst: str, contrast_val: float = 1.15, brightness: float = 0.02) -> str:
    """Static contrast/brightness correction via the eq filter."""
    _run(["-i", src, "-vf", f"eq=contrast={contrast_val}:brightness={brightness}", dst])
    return dst
