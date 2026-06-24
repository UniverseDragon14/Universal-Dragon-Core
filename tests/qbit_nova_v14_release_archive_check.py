#!/usr/bin/env python3
from pathlib import Path
import hashlib
import os
import subprocess
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PACKAGER = ROOT / "tools" / "package-qbit-nova-release.sh"

def run_cmd(cmd, cwd=None):
    r = subprocess.run(
        cmd,
        cwd=cwd or ROOT,
        text=True,
        capture_output=True,
    )
    out = (r.stdout or "") + (r.stderr or "")
    if r.returncode != 0:
        print(out)
        raise SystemExit(r.returncode)
    return out

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

with tempfile.TemporaryDirectory(prefix="qbit_nova_v14_") as tmp:
    base = Path(tmp)
    out_dir = base / "artifacts"
    extract_dir = base / "extract"
    prefix = base / "prefix"

    built = run_cmd([str(PACKAGER), str(out_dir)])

    if "QBIT_NOVA_V14_RELEASE_ARCHIVE_BUILT" not in built:
        print(built)
        raise SystemExit("archive build marker missing")

    archives = sorted(out_dir.glob("qbit-nova-release-v1.4.0-dev-*.tar.gz"))
    if not archives:
        raise SystemExit("release archive missing")

    archive = archives[-1]
    checksum = Path(str(archive) + ".sha256")

    manifests = sorted(out_dir.glob("QBIT_NOVA_RELEASE_MANIFEST_v1.4.0-dev_*.txt"))
    if not manifests:
        raise SystemExit("release manifest missing")

    if not checksum.exists():
        raise SystemExit("checksum file missing")

    expected_hash = checksum.read_text(encoding="utf-8").split()[0].strip()
    actual_hash = sha256_file(archive)

    if expected_hash != actual_hash:
        raise SystemExit("checksum mismatch")

    extract_dir.mkdir(parents=True, exist_ok=True)

    with tarfile.open(archive, "r:gz") as tar:
        tar.extractall(extract_dir)

    bundles = list(extract_dir.glob("qbit-nova-bundle-v1.4.0-dev-*"))
    if not bundles:
        raise SystemExit("extracted bundle missing")

    bundle = bundles[0]
    installer = bundle / "tools" / "install-qbit-nova.sh"
    launcher = prefix / "bin" / "qbit-nova"
    world = bundle / "examples" / "v2" / "qbit_nova_world.ud"
    src = bundle / "examples" / "v2" / "qbit_nova_v07_native_zero.ud"

    install_out = run_cmd([str(installer), "--prefix", str(prefix)], cwd=bundle)

    if "QBIT_NOVA_V12_INSTALLER_GREEN" not in install_out:
        print(install_out)
        raise SystemExit("installer marker missing from extracted archive")

    if not launcher.exists():
        raise SystemExit("launcher missing after extracted archive install")

    if not os.access(launcher, os.X_OK):
        raise SystemExit("launcher not executable after extracted archive install")

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

print("QBIT_NOVA_V14_RELEASE_ARCHIVE_GREEN")
