from pathlib import Path

files = [
    Path('docs/QBIT_NOVA_PROCESSOR_BRIDGE_CONCEPT_V0_1.md'),
    Path('examples/v2/qbit_nova_processor_bridge_v01.qnova'),
]

for p in files:
    if not p.exists():
        raise SystemExit(f'MISSING: {p}')

blob = '\n'.join(p.read_text(encoding='utf-8') for p in files)

checks = [
    'QBIT_NOVA_PROCESSOR_BRIDGE_V01',
    'QBIT',
    'QDOT',
    'QSTATE',
    'QLINK',
    'QPULSE',
    'QVM',
    'QBC',
    'QBRIDGE',
    'QPU Adapter',
    'no_fake_quantum_claim',
    'normal_cpu_bridge_now',
    'quantum_adapter_future',
    'source.tokenizer.parser.ast.ir.qvm.qbc.cpu',
    'Huawei Pura 70',
    'iPhone 16 Pro Max',
    'Raspberry Pi 5',
]

for c in checks:
    if c not in blob:
        raise SystemExit(f'MISSING MARKER: {c}')

print('QBIT_NOVA_PROCESSOR_BRIDGE_V01_GREEN')
