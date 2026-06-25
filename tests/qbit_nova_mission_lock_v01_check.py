from pathlib import Path

files = [
    Path('docs/QBIT_NOVA_MISSION_LOCK_V0_1.md'),
    Path('examples/v2/qbit_nova_mission_lock_v01.qnova'),
]

for p in files:
    if not p.exists():
        raise SystemExit(f'MISSING: {p}')

blob = '\n'.join(p.read_text(encoding='utf-8') for p in files)

checks = [
    'QBIT_NOVA_MISSION_LOCK_V01',
    'understand_typo_meaning',
    'No delete-first action',
    'Huawei Pura 70',
    'iPhone 16 Pro Max',
    'Raspberry Pi 5',
    'DNA',
    'Tokenizer',
    'Parser',
    'AST',
]

for c in checks:
    if c not in blob:
        raise SystemExit(f'MISSING MARKER: {c}')

print('QBIT_NOVA_MISSION_LOCK_V01_GREEN')
