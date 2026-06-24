# QBIT NOVA Tokenizer Pipeline v0.8

UD means Universal Dragon.

Creator: Aslam
Team: Askutty
Brain: NovaKutty
Language: QBIT NOVA
Source extension: .ud

## Purpose

QBIT NOVA v0.8 adds the tokenizer / lexer stage.

This moves QBIT NOVA closer to its own language engine.

Python is still only the bootstrap host.
The visible language identity remains QBIT NOVA.

## v0.8 Pipeline

.ud source
-> TOKENS
-> AST
-> QBIT_IR
-> QVM runtime
-> safe adapter contract

## Engine Files

engine/qbit_nova_v08_tokenizer.py
engine/qbit_nova_v08_pipeline.py

## Proof Tests

tests/qbit_nova_v08_tokenizer_check.py
tests/qbit_nova_v08_pipeline_check.py

## Success Markers

QBIT_NOVA_V08_TOKENIZER_CONTRACT_GREEN
QBIT_NOVA_V08_PIPELINE_CONTRACT_GREEN
QBIT_NOVA_V08_PIPELINE_GREEN
