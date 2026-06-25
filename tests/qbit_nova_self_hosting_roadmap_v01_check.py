from pathlib import Path

files = [
    Path('docs/QBIT_NOVA_SELF_HOSTING_ROADMAP_V0_1.md'),
    Path('examples/v2/qbit_nova_self_hosting_roadmap_v01.qnova'),
]

for p in files:
    if not p.exists():
        raise SystemExit(f'MISSING: {p}')

blob = '\n'.join(p.read_text(encoding='utf-8') for p in files)

checks = [
    'QBIT_NOVA_SELF_HOSTING_ROADMAP_V01',
    'Python is only a temporary bootstrap construction tool',
    'QBIT NOVA tools written in QBIT NOVA',
    'python_bootstrap_only',
    'qbit_nova_identity_only',
    'no_fake_independence',
    'qnova_reads_qnova',
    'qnova_compiles_qnova',
    'self_hosting_green',
]

for c in checks:
    if c not in blob:
        raise SystemExit(f'MISSING MARKER: {c}')

print('QBIT_NOVA_SELF_HOSTING_ROADMAP_V01_GREEN')
