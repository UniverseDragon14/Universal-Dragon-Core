#!/usr/bin/env python3
"""Carry-On gateway client — signs and sends one request.

Usage:
    export CARRYON_GATEWAY_SECRET="...same secret as server..."
    python -m carryon.carryon_gateway.client ping
    python -m carryon.carryon_gateway.client status
    python -m carryon.carryon_gateway.client nova_guard_shield --param shield=firewall --approve
    python -m carryon.carryon_gateway.client media --param 'argv=["probe","in.mp4"]'

Params are key=value; the value is parsed as JSON when possible, else kept as a
string. Diagnostics go to stderr; the JSON response is printed to stdout.
"""
from __future__ import annotations

import argparse
import json
import os
import secrets
import socket
import sys
import time

from carryon.carryon_gateway.server import SOCK_PATH, TCP_HOST, TCP_PORT, get_secret, sign


def _parse_param(item: str):
    key, _, raw = item.partition("=")
    try:
        return key, json.loads(raw)
    except json.JSONDecodeError:
        return key, raw


def build_request(action: str, params: dict, approval: bool) -> dict:
    req = {
        "action": action,
        "params": params,
        "ts": time.time(),
        "nonce": secrets.token_hex(16),
        "approval": approval,
    }
    req["sig"] = sign(req)
    return req


def send(req: dict) -> dict:
    if TCP_HOST:
        sock = socket.create_connection((TCP_HOST, TCP_PORT), timeout=65)
    else:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(65)
        sock.connect(SOCK_PATH)
    with sock:
        sock.sendall((json.dumps(req) + "\n").encode("utf-8"))
        buf = b""
        while not buf.endswith(b"\n"):
            chunk = sock.recv(4096)
            if not chunk:
                break
            buf += chunk
    return json.loads(buf.decode("utf-8") or "{}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="carryon-gw")
    p.add_argument("action")
    p.add_argument("--param", action="append", default=[], help="key=value (value JSON-parsed)")
    p.add_argument("--approve", action="store_true", help="authorize a needs_approval action")
    args = p.parse_args(argv)

    try:
        get_secret()
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    params = dict(_parse_param(x) for x in args.param)
    req = build_request(args.action, params, args.approve)
    resp = send(req)
    print(json.dumps(resp, indent=2))
    return 0 if resp.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
