#!/usr/bin/env python3
"""OpenCV-backed dynamic frame-contrast correction.

FFmpeg's eq filter applies a static curve. This module does *per-frame adaptive*
contrast (CLAHE on the L channel of LAB), which handles clips whose lighting
changes shot to shot. cv2 is imported lazily so the rest of the media pipeline
still works on a box without OpenCV installed.
"""
from __future__ import annotations

from carryon.common.log import get_logger

MARKER = "CARRYON_MEDIA_OPENCV_V01"
VERSION = "0.1.0"

log = get_logger("media.opencv")


def _cv2():
    import cv2  # lazy: keeps the pipeline importable without OpenCV present
    return cv2


def correct_frame(frame, clip_limit: float = 2.0, tile: int = 8):
    """Adaptive contrast on a single BGR frame using CLAHE in LAB space."""
    cv2 = _cv2()
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile, tile))
    l = clahe.apply(l)
    return cv2.cvtColor(cv2.merge((l, a, b)), cv2.COLOR_LAB2BGR)


def correct_video(src: str, dst: str, clip_limit: float = 2.0, tile: int = 8) -> str:
    """Apply adaptive contrast to every frame of a video, preserving fps/size.

    Writes silent video (OpenCV drops audio). If you need audio, run this first,
    then mux the original track back with ffmpeg_ops. Returns dst.
    """
    cv2 = _cv2()
    cap = cv2.VideoCapture(src)
    if not cap.isOpened():
        raise RuntimeError(f"cannot open video: {src}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(dst, fourcc, fps, (w, h))
    log.info("opencv contrast start", src=src, w=w, h=h, fps=round(fps, 2))
    count = 0
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            writer.write(correct_frame(frame, clip_limit, tile))
            count += 1
    finally:
        cap.release()
        writer.release()
    log.info("opencv contrast done", frames=count, dst=dst)
    return dst


def correct_image(src: str, dst: str, clip_limit: float = 2.0, tile: int = 8) -> str:
    """Adaptive contrast on a single still image."""
    cv2 = _cv2()
    img = cv2.imread(src)
    if img is None:
        raise RuntimeError(f"cannot read image: {src}")
    cv2.imwrite(dst, correct_frame(img, clip_limit, tile))
    return dst
