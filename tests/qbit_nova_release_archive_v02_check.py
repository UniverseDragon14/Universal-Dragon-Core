from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]

doc = ROOT / 'docs' / 'QBIT_NOVA_RELEASE_ARCHIVE_V0_2.md'
script = ROOT / 'tools' / 'package_qbit_nova_v02_release.sh'

for p in [doc, script]:
    if not p.exists():
        raise SystemExit(f'MISSING: {p}')

text = doc.read_text(encoding='utf-8')
for marker in [
    'QBIT_NOVA_RELEASE_ARCHIVE_V02',
    './tools/qnova',
    'portable archive',
]:
    if marker not in text:
        raise SystemExit(f'MISSING DOC MARKER: {marker}')

run = subprocess.run(
    [str(script)],
    cwd=str(ROOT),
    text=True,
    capture_output=True,
)

if run.returncode != 0:
    raise SystemExit(run.stdout + run.stderr)

out = run.stdout + run.stderr

for marker in [
    'QBIT_NOVA_RELEASE_ARCHIVE_V02',
    'QBIT_NOVA_RELEASE_ARCHIVE_V02_GREEN',
]:
    if marker not in out:
        raise SystemExit(f'MISSING OUTPUT MARKER: {marker}')

archive = ROOT / 'dist' / 'qbit-nova-v02-release.tar.gz'
sha = ROOT / 'dist' / 'qbit-nova-v02-release.sha256'

if not archive.exists():
    raise SystemExit('MISSING ARCHIVE')

if not sha.exists():
    raise SystemExit('MISSING SHA256')

print('QBIT_NOVA_RELEASE_ARCHIVE_V02_GREEN')
