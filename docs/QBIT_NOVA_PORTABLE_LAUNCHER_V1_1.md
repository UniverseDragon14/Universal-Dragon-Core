# QBIT NOVA Portable Launcher v1.1

UD means Universal Dragon.

Creator: Aslam
Team: Askutty
Brain: NovaKutty
Language: QBIT NOVA
Source extension: .ud

## Purpose

QBIT NOVA v1.1 adds a portable launcher.

This allows users to run QBIT NOVA through:

./tools/qbit-nova doctor
./tools/qbit-nova native <file.ud>
./tools/qbit-nova tokens <file.ud>
./tools/qbit-nova ast-native <file.ud>
./tools/qbit-nova ir <file.ud>

## Why this matters

Before v1.1, the user could run the engine through the internal nova CLI or Python paths.

With v1.1, QBIT NOVA has a portable repository launcher.

Python remains only the bootstrap host.
The visible identity remains QBIT NOVA.

## Engine Route

.ud source
-> TOKENS
-> TOKEN_PARSER_AST
-> SEMANTIC
-> QBIT_IR
-> QVM runtime
-> safe adapter contract

## Launcher File

tools/qbit-nova

## Proof Test

tests/qbit_nova_v11_portable_launcher_check.py

## Success Marker

QBIT_NOVA_V11_PORTABLE_LAUNCHER_GREEN
