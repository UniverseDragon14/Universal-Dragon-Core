#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
DOC = ROOT / "docs" / "QBIT_NOVA_QN_MANIFEST_RUNNER_V0_3.md"
INSTALL_QN = ROOT / "examples" / "v2" / "qbit_nova_install_v03.qn"
HELLO_QN = ROOT / "examples" / "v2" / "hello_qn_v03.qn"
MISSION_QN = ROOT / "examples" / "v2" / "mission_qn_v03.qn"

OUT_DIR = ROOT / ".tmp" / "qn-manifest-v03"

if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import qbit_nova_qn_manifest_runner_v03 as manifest_runner

for p in [
    DOC,
    TOOLS / "qbit_nova_qn_manifest_runner_v03.py",
    TOOLS / "qbit_nova_qbc_file_runner_v03.py",
    INSTALL_QN,
    HELLO_QN,
    MISSION_QN,
]:
    if not p.exists():
        raise SystemExit(f"MISSING: {p}")

doc = DOC.read_text(encoding="utf-8")

for marker in [
    "QBIT_NOVA_QN_MANIFEST_RUNNER_V03",
    "intent",
    "target",
    "package",
    "output marker",
    "must not directly execute OS install actions",
    "must not delete files",
    "./tools/qnova manifest source.qn",
]:
    if marker not in doc:
        raise SystemExit(f"MISSING DOC MARKER: {marker}")

def check_manifest(src: Path, out_name: str, expected_output: str, expected_intent: str, expected_target=None, expected_package=None):
    out = OUT_DIR / out_name
    result = manifest_runner.run_manifest(src, out)

    if result.get("marker") != "QBIT_NOVA_QN_MANIFEST_RUNNER_V03":
        raise SystemExit("BAD MANIFEST RUNNER MARKER")

    if result.get("mode") != "SAFE_QN_MANIFEST_READ":
        raise SystemExit("BAD MANIFEST MODE")

    if result.get("success") is not True:
        raise SystemExit("MANIFEST SUCCESS NOT TRUE")

    if result.get("decoded_output") != expected_output:
        raise SystemExit(f"BAD DECODED OUTPUT: {result.get('decoded_output')}")

    manifest = result.get("manifest", {})

    if manifest.get("intent") != expected_intent:
        raise SystemExit(f"BAD INTENT: {manifest.get('intent')}")

    if expected_target is not None and manifest.get("target") != expected_target:
        raise SystemExit(f"BAD TARGET: {manifest.get('target')}")

    if expected_package is not None and manifest.get("package") != expected_package:
        raise SystemExit(f"BAD PACKAGE: {manifest.get('package')}")

    if manifest.get("safe_stage") is not True:
        raise SystemExit("SAFE STAGE NOT TRUE")

    if manifest.get("os_execution") is not False:
        raise SystemExit("OS EXECUTION MUST BE FALSE")

    if manifest.get("delete_action") is not False:
        raise SystemExit("DELETE ACTION MUST BE FALSE")

    qbc = Path(result["qbc"])
    if not qbc.exists():
        raise SystemExit(f"MISSING QBC: {qbc}")

    qbc_text = qbc.read_text(encoding="utf-8")
    if "FF" in qbc_text.split():
        raise SystemExit("UNKNOWN OPCODE FF FOUND")

check_manifest(
    INSTALL_QN,
    "install_manifest_v03.qbc",
    "QBIT_NOVA_INSTALL_QN_V03",
    "install_qbit_nova",
    "local_user_bin",
    "qnova",
)

check_manifest(
    HELLO_QN,
    "hello_manifest_v03.qbc",
    "QBIT_NOVA_QN_HELLO_V03",
    "hello_qn",
)

check_manifest(
    MISSION_QN,
    "mission_manifest_v03.qbc",
    "QBIT_NOVA_MISSION_QN_V03",
    "mission_lock",
    "qbit_core",
    "manifest_runner",
)

print("QBIT_NOVA_QN_MANIFEST_RUNNER_V03_GREEN")
