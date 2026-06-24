# QBIT NOVA Installer v1.2

UD means Universal Dragon.

Creator: Aslam
Team: Askutty
Brain: NovaKutty
Language: QBIT NOVA
Source extension: .ud

## Purpose

QBIT NOVA v1.2 adds an installer script.

This allows users to install the QBIT NOVA launcher into a bin folder and run it as:

qbit-nova doctor
qbit-nova native <file.ud>
qbit-nova tokens <file.ud>
qbit-nova ast-native <file.ud>
qbit-nova ir <file.ud>

## Installer

tools/install-qbit-nova.sh

## Example

./tools/install-qbit-nova.sh --prefix "$HOME/.local"

Then run:

$HOME/.local/bin/qbit-nova doctor

## Engine Route

.ud source
-> TOKENS
-> TOKEN_PARSER_AST
-> SEMANTIC
-> QBIT_IR
-> QVM runtime
-> safe adapter contract

## Proof Test

tests/qbit_nova_v12_installer_check.py

## Success Markers

V12_INSTALLER_SYNTAX_GREEN
QBIT_NOVA_V12_INSTALLER_GREEN
QBIT_NOVA_V12_INSTALLER_CONTRACT_GREEN
