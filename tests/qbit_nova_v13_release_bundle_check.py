#!/usr/bin/env python3
from pathlib import Path
import os
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "tools" / "build-qbit-nova-bundle.sh"

def run_cmd(cmd, cwd=None):
    r = subprocess.run(cmd, cwd=cwd or ROOT, text=True, capture_output=True)
    out = (r.stdout or "") + (r.stderr or "")
    if r.returncode != 0:
        print(out)
        raise SystemExit(r.returncode)
    return out

with tempfile.TemporaryDirectory(prefix="qbit_nova_v13_") as tmp:
    base = Path(tmp)
    bundle = base / "bundle"
    prefix = base / "prefix"

    built = run_cmd([str(BUILDER), str(bundle)])

    if "QBIT_NOVA_V13_BUNDLE_BUILT" not in built:
        print(built)
        raise SystemExit("bundle build marker missing")

    required = [
        "README.md",
        "NOVA_QBIT_VERSION",
        "tools/nova_cli.ud",
        "tools/qbit-nova",
        "tools/install-qbit-nova.sh",
        "engine/qbit_nova_v07_engine.py",
        "engine/qbit_nova_v08_tokenizer.py",
        "engine/qbit_nova_v09_token_parser.py",
        "engine/qbit_nova_v09_pipeline.py",
        "nova-lang/v2/nova2_run.py",
        "nova-lang/v2/nova2_seed.py",
        "nova-lang/v2/nova2_quantum_syntax.py",
        "examples/v2/qbit_nova_world.ud",
        "examples/v2/qbit_nova_v07_native_zero.ud",
    ]

    for rel in required:
        if not (bundle / rel).exists():
            raise SystemExit(f"bundle missing: {rel}")

    installer = bundle / "tools" / "install-qbit-nova.sh"
    launcher = prefix / "bin" / "qbit-nova"
    world = bundle / "examples" / "v2" / "qbit_nova_world.ud"
    src = bundle / "examples" / "v2" / "qbit_nova_v07_native_zero.ud"

    install_out = run_cmd([str(installer), "--prefix", str(prefix)], cwd=bundle)

    if "QBIT_NOVA_V12_INSTALLER_GREEN" not in install_out:
        print(install_out)
        raise SystemExit("installer marker missing")

    if not launcher.exists():
        raise SystemExit("launcher missing")

    if not os.access(launcher, os.X_OK):
        raise SystemExit("launcher not executable")

    doctor = run_cmd([str(launcher), "doctor"], cwd=bundle)
    run_world = run_cmd([str(launcher), "run", str(world)], cwd=bundle)
    ir = run_cmd([str(launcher), "ir", str(src)], cwd=bundle)

    checks = [
        (doctor, "QBIT NOVA doctor"),
        (doctor, "Runner  : OK"),
        (run_world, "QBIT NOVA language online"),
        (run_world, "guard block loaded"),
        (ir, "QBIT_NOVA_V10_IR_GREEN"),
    ]

    for output, marker in checks:
        if marker not in output:
            print(output)
            raise SystemExit(f"missing marker: {marker}")

print("QBIT_NOVA_V13_RELEASE_BUNDLE_GREEN")
