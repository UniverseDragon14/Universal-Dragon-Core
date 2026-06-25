#!/usr/bin/env python3
from pathlib import Path
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
DOC = ROOT / "docs" / "QBIT_NOVA_QNOVA_MANIFEST_COMMAND_V0_3.md"
QNOVA = TOOLS / "qnova"
INSTALL_QN = ROOT / "examples" / "v2" / "qbit_nova_install_v03.qn"
OUT_DIR = ROOT / ".tmp" / "qnova-manifest-v03"
DEFAULT_OUT = OUT_DIR / "qbit_nova_install_v03.qbc"

for p in [
    DOC,
    QNOVA,
    TOOLS / "qbit_nova_qn_manifest_runner_v03.py",
    TOOLS / "qbit_nova_qbc_file_runner_v03.py",
    INSTALL_QN,
]:
    if not p.exists():
        raise SystemExit(f"MISSING: {p}")

doc = DOC.read_text(encoding="utf-8")
for marker in [
    "QBIT_NOVA_QNOVA_MANIFEST_COMMAND_V03",
    "QBIT_NOVA_QNOVA_MANIFEST_COMMAND_V03_GREEN",
    "./tools/qnova manifest source.qn",
    ".tmp/qnova-manifest-v03/<source_stem>.qbc",
    "SAFE_QN_MANIFEST_READ",
    "must not directly execute OS install actions",
    "must not delete files",
    "must not read secrets",
    "FF opcode",
]:
    if marker not in doc:
        raise SystemExit(f"MISSING DOC MARKER: {marker}")


def parse_command_json(stdout: str) -> dict:
    start = stdout.find("{")
    end = stdout.rfind("}")
    if start == -1 or end == -1 or end < start:
        print(stdout)
        raise SystemExit("MISSING COMMAND JSON")
    return json.loads(stdout[start : end + 1])


def run_manifest_command(src: Path, out: Path | None = None) -> dict:
    cmd = [str(QNOVA), "manifest", str(src)]
    if out is not None:
        cmd.append(str(out))

    result = subprocess.run(
        cmd,
        cwd=str(ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    if result.returncode != 0:
        print(result.stdout)
        raise SystemExit(f"QNOVA MANIFEST COMMAND FAILED: {src}")

    for marker in [
        "QBIT_NOVA_QNOVA_MANIFEST_COMMAND_V03",
        "QBIT_NOVA_QNOVA_MANIFEST_COMMAND_V03_GREEN",
        "QBIT_NOVA_QN_MANIFEST_RUNNER_V03",
    ]:
        if marker not in result.stdout:
            print(result.stdout)
            raise SystemExit(f"MISSING COMMAND MARKER: {marker}")

    payload = parse_command_json(result.stdout)

    if payload.get("mode") != "SAFE_QN_MANIFEST_READ":
        raise SystemExit(f"BAD MANIFEST MODE: {payload.get('mode')}")

    if payload.get("runner_marker") != "QBIT_NOVA_QN_MANIFEST_RUNNER_V03":
        raise SystemExit(f"BAD RUNNER MARKER: {payload.get('runner_marker')}")

    manifest = payload.get("manifest", {})
    if manifest.get("os_execution") is not False:
        raise SystemExit("OS EXECUTION MUST BE FALSE")

    if manifest.get("delete_action") is not False:
        raise SystemExit("DELETE ACTION MUST BE FALSE")

    qbc = Path(payload["qbc"])
    if not qbc.exists():
        raise SystemExit(f"MISSING QBC: {qbc}")

    qbc_text = qbc.read_text(encoding="utf-8")
    if "FF" in qbc_text.split():
        raise SystemExit("UNKNOWN OPCODE FF FOUND")

    return payload


payload = run_manifest_command(INSTALL_QN)
if Path(payload["qbc"]) != DEFAULT_OUT:
    raise SystemExit(f"BAD DEFAULT OUTPUT: {payload['qbc']}")

for suffix in [".json", ".pool.json", ".expanded.qnova"]:
    p = Path(str(DEFAULT_OUT) + suffix)
    if not p.exists():
        raise SystemExit(f"MISSING OUTPUT SIDE FILE: {p}")
    if p.stat().st_size <= 0:
        raise SystemExit(f"EMPTY OUTPUT SIDE FILE: {p}")

for ext in [".qnova", ".ud"]:
    src = OUT_DIR / f"qbit_nova_install_v03_manifest_command{ext}"
    out = OUT_DIR / f"qbit_nova_install_v03_manifest_command{ext}.qbc"
    src.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(INSTALL_QN, src)
    run_manifest_command(src, out)

print("QBIT_NOVA_QNOVA_MANIFEST_COMMAND_V03_GREEN")
