#!/usr/bin/env python3
"""Carry-On Terminal Command Gateway (server).

A local, authenticated control plane. It listens on a Unix domain socket (or a
loopback TCP port) and accepts newline-delimited JSON requests. Security model,
in layers:

  1. Transport    : Unix socket with 0600 perms (owner-only) by default. No
                    default exposure to the network at all.
  2. Authenticity : every request carries an HMAC-SHA256 signature over its
                    canonical bytes using a shared secret (CARRYON_GATEWAY_SECRET
                    or a 0600 key file). Bad signature -> rejected, nothing runs.
  3. Freshness    : requests include a unix `ts` and random `nonce`. Stale
                    timestamps (outside +/- window) and replayed nonces are
                    rejected, so a captured request cannot be replayed.
  4. Authorization: the action name must be in the allowlist AND pass Nova Guard.
                    "blocked" -> refused; "needs_approval" -> refused unless the
                    request is explicitly signed with approval=true by the operator.

This is deliberately the opposite of a "hidden backdoor": it is a small, signed,
auditable surface. Obscurity is not used as a control anywhere.

Request  (one JSON object per line):
    {"action": "...", "params": {...}, "ts": 1720000000.0,
     "nonce": "hex", "approval": false, "sig": "hmac-hex"}
Response:
    {"ok": true|false, "decision": "...", "result"|"error": ...}

Run:
    python -m carryon.carryon_gateway.server
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import socket
import socketserver
import threading
import time

from carryon.common.log import get_logger
from carryon.carryon_gateway import actions as action_mod
from carryon.carryon_gateway import guard as guard_mod

MARKER = "CARRYON_GATEWAY_SERVER_V01"
VERSION = "0.1.0"

log = get_logger("gateway.server")

SOCK_PATH = os.environ.get("CARRYON_GATEWAY_SOCK", "/tmp/carryon-gateway.sock")
TCP_HOST = os.environ.get("CARRYON_GATEWAY_HOST")  # set to 127.0.0.1 to use TCP
TCP_PORT = int(os.environ.get("CARRYON_GATEWAY_PORT", "8787"))
TS_WINDOW = int(os.environ.get("CARRYON_GATEWAY_TS_WINDOW", "30"))  # seconds

_nonce_lock = threading.Lock()
_seen_nonces: dict[str, float] = {}


_secret_cache: bytes | None = None


def get_secret() -> bytes:
    """Resolve the shared HMAC secret lazily (env first, then key file).

    Loaded on first use, not at import, so the module imports cleanly in tests
    and the client can reuse this without a secret being present for imports.
    """
    global _secret_cache
    if _secret_cache is not None:
        return _secret_cache
    secret = os.environ.get("CARRYON_GATEWAY_SECRET")
    if secret:
        _secret_cache = secret.encode("utf-8")
        return _secret_cache
    key_file = os.environ.get("CARRYON_GATEWAY_KEYFILE")
    if key_file and os.path.exists(key_file):
        with open(key_file, "rb") as fh:
            _secret_cache = fh.read().strip()
        return _secret_cache
    raise RuntimeError(
        "No gateway secret. Set CARRYON_GATEWAY_SECRET or CARRYON_GATEWAY_KEYFILE."
    )


def canonical(req: dict) -> bytes:
    """Bytes that the signature covers. Excludes the sig field itself."""
    payload = {
        "action": req.get("action"),
        "params": req.get("params", {}),
        "ts": req.get("ts"),
        "nonce": req.get("nonce"),
        "approval": bool(req.get("approval", False)),
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sign(req: dict) -> str:
    return hmac.new(get_secret(), canonical(req), hashlib.sha256).hexdigest()


def _verify(req: dict) -> tuple[bool, str]:
    sig = req.get("sig", "")
    expected = sign(req)
    if not hmac.compare_digest(sig, expected):
        return False, "bad signature"

    ts = req.get("ts")
    if not isinstance(ts, (int, float)) or abs(time.time() - ts) > TS_WINDOW:
        return False, "stale or missing timestamp"

    nonce = req.get("nonce")
    if not nonce or not isinstance(nonce, str):
        return False, "missing nonce"
    now = time.time()
    with _nonce_lock:
        # prune old nonces beyond the freshness window
        for n, seen in list(_seen_nonces.items()):
            if now - seen > TS_WINDOW * 2:
                _seen_nonces.pop(n, None)
        if nonce in _seen_nonces:
            return False, "replayed nonce"
        _seen_nonces[nonce] = now
    return True, ""


def handle_request(req: dict) -> dict:
    ok, why = _verify(req)
    if not ok:
        log.warn("request rejected", reason=why, action=req.get("action"))
        return {"ok": False, "error": f"auth: {why}"}

    action = req.get("action")
    if action not in action_mod.REGISTRY:
        return {"ok": False, "error": f"unknown action: {action}"}

    category = action_mod.ACTION_GUARD_CATEGORY.get(action, "unknown")
    decision = guard_mod.evaluate(category)
    verdict = decision["decision"]

    if verdict == "blocked":
        log.warn("action blocked by guard", action=action, category=category)
        return {"ok": False, "decision": verdict, "error": decision["reason"]}

    if verdict == "needs_approval" and not req.get("approval", False):
        log.warn("action needs approval", action=action, category=category)
        return {"ok": False, "decision": verdict, "error": decision["reason"],
                "hint": "re-send with approval=true (must be signed) to authorize"}

    try:
        result = action_mod.REGISTRY[action](req.get("params", {}))
        log.info("action executed", action=action, decision=verdict)
        return {"ok": True, "decision": verdict, "result": result}
    except Exception as exc:
        log.error("action failed", action=action, error=str(exc))
        return {"ok": False, "decision": verdict, "error": str(exc)}


class _Handler(socketserver.StreamRequestHandler):
    def handle(self) -> None:
        for raw in self.rfile:
            line = raw.strip()
            if not line:
                continue
            try:
                req = json.loads(line)
            except json.JSONDecodeError:
                self.wfile.write(b'{"ok":false,"error":"invalid json"}\n')
                continue
            resp = handle_request(req)
            self.wfile.write((json.dumps(resp) + "\n").encode("utf-8"))
            self.wfile.flush()


class _ThreadingUnixServer(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    daemon_threads = True
    allow_reuse_address = True


class _ThreadingTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True
    allow_reuse_address = True


def serve() -> None:
    get_secret()  # fail fast if no secret is configured before binding anything
    if TCP_HOST:
        if TCP_HOST not in ("127.0.0.1", "::1", "localhost"):
            # Refuse to bind a non-loopback address; this stays a LOCAL gateway.
            raise RuntimeError(f"refusing non-loopback bind: {TCP_HOST}")
        server = _ThreadingTCPServer((TCP_HOST, TCP_PORT), _Handler)
        log.info("gateway online (tcp)", host=TCP_HOST, port=TCP_PORT, ts_window=TS_WINDOW)
    else:
        if os.path.exists(SOCK_PATH):
            os.unlink(SOCK_PATH)
        server = _ThreadingUnixServer(SOCK_PATH, _Handler)
        os.chmod(SOCK_PATH, 0o600)  # owner-only access to the control socket
        log.info("gateway online (unix)", sock=SOCK_PATH, ts_window=TS_WINDOW)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log.info("gateway shutting down")
    finally:
        server.server_close()
        if not TCP_HOST and os.path.exists(SOCK_PATH):
            os.unlink(SOCK_PATH)


if __name__ == "__main__":
    serve()
