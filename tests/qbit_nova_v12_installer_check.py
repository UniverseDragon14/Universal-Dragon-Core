#!/usr/bin/env python3
from pathlib import Path
import os
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "tools" / "install-qbit-nova.sh"
SRC = ROOT / "examples" / "v2" / "qbit_nova_v07_native_zero.ud"

def run_cmd(cmd, cwd=ROOT):
    r = subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        capture_output=True,
    )
    out = (r.stdout or "") + (r.stderr or "")
    if r.returncode != 0:
        print(out)
        raise SystemExit(r.returncode)
    return out

with tempfile.TemporaryDirectory(prefix="qbit_nova_install_") as tmp:
    prefix = Path(tmp)
    out = run_cmd([str(INSTALLER), "--prefix", str(prefix)])

    launcher = prefix / "bin" / "qbit-nova"

    if "QBIT_NOVA_V12_INSTALLER_GREEN" not in out:
        print(out)
        raise SystemExit("installer marker missing")

    if not launcher.exists():
        raise SystemExit("installed launcher missing")

    if not os.access(launcher, os.X_OK):
        raise SystemExit("installed launcher not executable")

    doctor = run_cmd([str(launcher), "doctor"])
    native = run_cmd([str(launcher), "native", str(SRC)])
    tokens = run_cmd([str(launcher), "tokens", str(SRC)])
    ast_native = run_cmd([str(launcher), "ast-native", str(SRC)])
    ir = run_cmd([str(launcher), "ir", str(SRC)])

    checks = [
        (doctor, "QBIT NOVA doctor"),
        (native, "QBIT_NOVA_V09_PIPELINE_GREEN"),
        (tokens, "QBIT_NOVA_V08_TOKENIZER_GREEN"),
        (ast_native, "QBIT_NOVA_V09_TOKEN_PARSER_GREEN"),
        (ir, "QBIT_NOVA_V10_IR_GREEN"),
    ]

    for output, marker in checks:
        if marker not in output:
            print(output)
            raise SystemExit(f"missing marker: {marker}")

print("QBIT_NOVA_V12_INSTALLER_CONTRACT_GREEN")
