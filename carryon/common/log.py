#!/usr/bin/env python3
"""MCP-safe logging for the Carry-On core.

Every diagnostic line goes to sys.stderr so that sys.stdout stays a clean
JSON-RPC channel for MCP stdio transports. Never print() logs to stdout in
any Carry-On module; import get_logger from here instead.
"""
from __future__ import annotations

import json
import os
import sys
import time

MARKER = "CARRYON_COMMON_LOG_V01"
VERSION = "0.1.0"

_LEVELS = {"debug": 10, "info": 20, "warn": 30, "error": 40}
_THRESHOLD = _LEVELS.get(os.environ.get("CARRYON_LOG_LEVEL", "info").lower(), 20)


class Logger:
    def __init__(self, name: str) -> None:
        self.name = name

    def _emit(self, level: str, msg: str, **fields: object) -> None:
        if _LEVELS[level] < _THRESHOLD:
            return
        record = {
            "ts": round(time.time(), 3),
            "level": level,
            "logger": self.name,
            "msg": msg,
        }
        if fields:
            record["fields"] = fields
        # stderr ONLY. Keeping stdout pristine is a hard requirement for MCP.
        print(json.dumps(record, ensure_ascii=False), file=sys.stderr, flush=True)

    def debug(self, msg: str, **f: object) -> None:
        self._emit("debug", msg, **f)

    def info(self, msg: str, **f: object) -> None:
        self._emit("info", msg, **f)

    def warn(self, msg: str, **f: object) -> None:
        self._emit("warn", msg, **f)

    def error(self, msg: str, **f: object) -> None:
        self._emit("error", msg, **f)


def get_logger(name: str) -> Logger:
    return Logger(name)
