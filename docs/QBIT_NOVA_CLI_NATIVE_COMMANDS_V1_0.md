# QBIT NOVA CLI Native Commands v1.0

UD means Universal Dragon.

Creator: Aslam
Team: Askutty
Brain: NovaKutty
Language: QBIT NOVA
Source extension: .ud

## Purpose

QBIT NOVA v1.0 exposes native language-engine commands through the `nova` CLI.

This makes QBIT NOVA user-facing instead of forcing the user to run Python engine files directly.

Python remains only the bootstrap host.
The visible identity remains QBIT NOVA.

## Commands

nova native <file.ud>
nova tokens <file.ud>
nova ast-native <file.ud>
nova ir <file.ud>

## Engine Route

.ud source
-> TOKENS
-> TOKEN_PARSER_AST
-> SEMANTIC
-> QBIT_IR
-> QVM runtime
-> safe adapter contract

## Proof

The CLI can now run:

nova native examples/v2/qbit_nova_v07_native_zero.ud
nova tokens examples/v2/qbit_nova_v07_native_zero.ud
nova ast-native examples/v2/qbit_nova_v07_native_zero.ud
nova ir examples/v2/qbit_nova_v07_native_zero.ud

## Success Markers

V10_CLI_SYNTAX_GREEN
QBIT_NOVA_V10_IR_GREEN
QBIT_NOVA_V10_CLI_NATIVE_CONTRACT_GREEN
