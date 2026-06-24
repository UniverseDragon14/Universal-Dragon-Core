# QBIT NOVA Native Engine Split v0.7

UD means Universal Dragon.

Creator: Aslam
Team: Askutty
Brain: NovaKutty
Language: QBIT NOVA
Source extension: .ud

Purpose:
QBIT NOVA must grow as its own language engine.

Python is currently only a bootstrap host.
The visible identity remains QBIT NOVA.

v0.7 pipeline:
.ud source
-> AST
-> QBIT_IR
-> QVM runtime
-> safe adapter contract

New engine:
engine/qbit_nova_v07_engine.py

This proves:
- parse .ud
- validate semantics
- compile to QBIT_IR
- run in QVM
- enforce safe adapter contract

Success:
QBIT_NOVA_V07_NATIVE_ENGINE_CONTRACT_GREEN
