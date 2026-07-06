#!/usr/bin/env python3
"""Local shell entrypoint for the media pipeline.

Every operation is a subcommand so you can trigger it from a plain shell,
a Termux alias, or the Carry-On gateway's `media` action.

Examples:
    python -m carryon.media_pipeline.cli probe in.mp4
    python -m carryon.media_pipeline.cli slice in.mp4 out.mp4 --start 5 --duration 10
    python -m carryon.media_pipeline.cli scale in.mp4 out.mp4 --width 1280
    python -m carryon.media_pipeline.cli denoise in.mp4 out.mp4
    python -m carryon.media_pipeline.cli contrast in.mp4 out.mp4          # ffmpeg static
    python -m carryon.media_pipeline.cli autocontrast in.mp4 out.mp4      # opencv adaptive
"""
from __future__ import annotations

import argparse
import json
import sys

from carryon.common.log import get_logger
from carryon.media_pipeline import ffmpeg_ops

log = get_logger("media.cli")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="carryon-media", description="Carry-On media pipeline")
    sub = p.add_subparsers(dest="cmd", required=True)

    pr = sub.add_parser("probe"); pr.add_argument("src")

    sl = sub.add_parser("slice")
    sl.add_argument("src"); sl.add_argument("dst")
    sl.add_argument("--start", type=float, required=True)
    sl.add_argument("--duration", type=float, required=True)

    sc = sub.add_parser("scale")
    sc.add_argument("src"); sc.add_argument("dst")
    sc.add_argument("--width", type=int, required=True)
    sc.add_argument("--height", type=int, default=-2)

    dn = sub.add_parser("denoise"); dn.add_argument("src"); dn.add_argument("dst")

    ct = sub.add_parser("contrast")
    ct.add_argument("src"); ct.add_argument("dst")
    ct.add_argument("--contrast", type=float, default=1.15)
    ct.add_argument("--brightness", type=float, default=0.02)

    ac = sub.add_parser("autocontrast")
    ac.add_argument("src"); ac.add_argument("dst")
    ac.add_argument("--clip", type=float, default=2.0)
    ac.add_argument("--tile", type=int, default=8)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.cmd == "probe":
            # probe result is data, so it is allowed on stdout as a JSON document
            print(json.dumps(ffmpeg_ops.probe(args.src)))
        elif args.cmd == "slice":
            ffmpeg_ops.slice_clip(args.src, args.dst, args.start, args.duration)
        elif args.cmd == "scale":
            ffmpeg_ops.scale(args.src, args.dst, args.width, args.height)
        elif args.cmd == "denoise":
            ffmpeg_ops.denoise(args.src, args.dst)
        elif args.cmd == "contrast":
            ffmpeg_ops.contrast(args.src, args.dst, args.contrast, args.brightness)
        elif args.cmd == "autocontrast":
            from carryon.media_pipeline import opencv_ops
            opencv_ops.correct_video(args.src, args.dst, args.clip, args.tile)
        log.info("done", cmd=args.cmd)
        return 0
    except Exception as exc:
        log.error("command failed", cmd=args.cmd, error=str(exc))
        return 1


if __name__ == "__main__":
    sys.exit(main())
