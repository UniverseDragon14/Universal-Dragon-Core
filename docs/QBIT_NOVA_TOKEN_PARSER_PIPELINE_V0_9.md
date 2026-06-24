# QBIT NOVA Token Parser Pipeline v0.9

UD means Universal Dragon.

Creator: Aslam
Team: Askutty
Brain: NovaKutty
Language: QBIT NOVA
Source extension: .ud

## Purpose

QBIT NOVA v0.9 adds a token-stream parser.

This means the AST is now produced from tokenizer output instead of only reading lines directly.

Python is still the bootstrap host.
The visible identity remains QBIT NOVA.

## v0.9 Pipeline

.ud source
-> TOKENS
-> TOKEN_PARSER_AST
-> SEMANTIC
-> QBIT_IR
-> QVM runtime
-> safe adapter contract

## Engine Files

engine/qbit_nova_v08_tokenizer.py
engine/qbit_nova_v09_token_parser.py
engine/qbit_nova_v09_pipeline.py

## Proof Tests

tests/qbit_nova_v09_token_parser_check.py
tests/qbit_nova_v09_pipeline_check.py

## Success Markers

QBIT_NOVA_V09_TOKEN_PARSER_CONTRACT_GREEN
QBIT_NOVA_V09_PIPELINE_CONTRACT_GREEN
QBIT_NOVA_V09_PIPELINE_GREEN
