from pathlib import Path

doc = Path('docs/QBIT_NOVA_RELEASE_CHECKPOINT_V0_2.md')

if not doc.exists():
    raise SystemExit('MISSING RELEASE CHECKPOINT DOC')

text = doc.read_text(encoding='utf-8')

checks = [
    'QBIT_NOVA_RELEASE_CHECKPOINT_V02',
    './tools/qnova',
    'Tokenizer',
    'Parser',
    'AST',
    'IR',
    'QVM',
    'QBC',
    'QBC Runner',
    'Full Runner',
    'CLI Launcher',
    'Huawei Pura 70',
    'self-hosting QBIT NOVA',
]

for c in checks:
    if c not in text:
        raise SystemExit(f'MISSING MARKER: {c}')

print('QBIT_NOVA_RELEASE_CHECKPOINT_V02_GREEN')
