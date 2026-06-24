# QBIT NOVA Grammar Contract v0.6 Semantic Checker

Creator: Aslam
Team: Askutty
Brain: NovaKutty
Language: QBIT NOVA
Source extension: .ud

## v0.6 Goal

QBIT NOVA v0.6 adds semantic checking.

Syntax means the file shape is readable.

Semantics means the logic is valid.

## Command

    nova check examples/v2/qbit_nova_v06_semantic_good.ud

## Checks

- creator must be Aslam
- team must be Askutty
- brain must be NovaKutty
- qbit must be declared
- qbit state must be valid
- gate target must exist
- measurement target must exist
- when block must use measured qbit
- adapter must follow safe contract

## Purpose

This is the compiler gate before real external adapters.

QBIT NOVA should understand, verify, and only then execute.
