#!/usr/bin/env python3
"""Allowlisted actions for the Carry-On gateway.

Design rule: the gateway NEVER runs arbitrary shell. It exposes a fixed set of
named actions, each with typed parameters and a Nova Guard category. Adding
capability means adding an entry here on purpose — not passing a command string
over the wire. This is the whole security posture: a small, auditable surface.

Each action returns a JSON-serializable dict. Diagnostics go to stderr.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time

from carryon.common.log import get_logger

MARKER = "CARRYON_GATEWAY_ACTIONS_V01"
VERSION = "0.1.0"

log = get_logger("gateway.actions")

# Where to find operator-approved shield/subagent scripts. Only files inside
# this directory may be launched, and only if listed in SHIELD_SCRIPTS.
BIN_DIR = os.environ.get("CARRYON_BIN_DIR", os.path.join(os.path.dirname(__file__), "..", "bin"))

# name -> Nova Guard category used for the approval decision
ACTION_GUARD_CATEGORY = {
    "ping": "check",
    "status": "check",
    "nova_guard_shield": "network",
    "launch_subagent": "install",
    "media": "write_file",
}

# Named shields the gateway may deploy. Value is a script basename in BIN_DIR.
SHIELD_SCRIPTS = {
    "firewall": "nova_guard_firewall.sh",
    "rate_limit": "nova_guard_rate_limit.sh",
}


def _safe_bin(basename: str) -> str:
    """Resolve a script strictly inside BIN_DIR; reject traversal."""
    root = os.path.abspath(BIN_DIR)
    candidate = os.path.abspath(os.path.join(root, basename))
    if os.path.commonpath([root, candidate]) != root:
        raise ValueError("script path escapes BIN_DIR")
    if not os.path.isfile(candidate):
        raise FileNotFoundError(f"shield script not present: {basename}")
    return candidate


def act_ping(_params: dict) -> dict:
    return {"pong": True, "ts": time.time()}


def act_status(_params: dict) -> dict:
    return {
        "ts": time.time(),
        "python": sys.version.split()[0],
        "ffmpeg": bool(shutil.which("ffmpeg")),
        "bin_dir": os.path.abspath(BIN_DIR),
        "shields": sorted(SHIELD_SCRIPTS),
    }


def act_nova_guard_shield(params: dict) -> dict:
    name = params.get("shield")
    if name not in SHIELD_SCRIPTS:
        raise ValueError(f"unknown shield: {name!r}; allowed: {sorted(SHIELD_SCRIPTS)}")
    script = _safe_bin(SHIELD_SCRIPTS[name])
    mode = "on" if params.get("enable", True) else "off"
    log.info("deploying shield", shield=name, mode=mode)
    proc = subprocess.run([script, mode], capture_output=True, text=True, timeout=60)
    return {"shield": name, "mode": mode, "rc": proc.returncode, "stdout": proc.stdout.strip()[:2000]}


def act_launch_subagent(params: dict) -> dict:
    name = params.get("name")
    if not name or not name.replace("_", "").replace("-", "").isalnum():
        raise ValueError("subagent name must be alphanumeric/_/-")
    script = _safe_bin(f"subagent_{name}.sh")
    log.info("launching subagent", name=name)
    # Detached background launch; the subagent script is operator-provided.
    proc = subprocess.Popen(
        [script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL, start_new_session=True,
    )
    return {"subagent": name, "pid": proc.pid}


def act_media(params: dict) -> dict:
    from carryon.media_pipeline import cli as media_cli
    argv = params.get("argv")
    if not isinstance(argv, list) or not all(isinstance(x, str) for x in argv):
        raise ValueError("media action requires argv: list[str]")
    rc = media_cli.main(argv)
    return {"cmd": "media", "argv": argv, "rc": rc}


REGISTRY = {
    "ping": act_ping,
    "status": act_status,
    "nova_guard_shield": act_nova_guard_shield,
    "launch_subagent": act_launch_subagent,
    "media": act_media,
}
