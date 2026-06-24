from pathlib import Path

required = [
    Path('docs/QBIT_NOVA_LANGUAGE_DNA_V0_1.md'),
    Path('examples/v2/qbit_nova_dna_v01.qnova'),
]

for p in required:
    if not p.exists():
        raise SystemExit(f'MISSING: {p}')

doc = required[0].read_text(encoding='utf-8')
src = required[1].read_text(encoding='utf-8')

checks = [
    'QBIT NOVA is a completely new',
    'bootstrap construction tools',
    'Own tokenizer',
    'Own parser',
    'Own QVM',
    'Self-hosting compiler',
    'QBIT_NOVA_LANGUAGE_DNA_V01',
    'law no_existing_language_identity',
    'guard intent',
    'rollback on_fail',
]

blob = doc + '\n' + src

for c in checks:
    if c not in blob:
        raise SystemExit(f'MISSING MARKER: {c}')

print('QBIT_NOVA_LANGUAGE_DNA_V01_GREEN')
