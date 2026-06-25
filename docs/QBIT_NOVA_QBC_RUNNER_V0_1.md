# QBIT NOVA QBC Runner v0.1

Creator: Aslam
Project: Universal Dragon
Brain: NovaKutty
Team: Askutty
Language: QBIT NOVA

## Purpose

This document locks the first QBIT NOVA QBC Runner contract.

QBC means QBIT Bytecode.
QBC Runner reads QBIT bytecode and rebuilds a safe execution trace.

## Truth Lock

QBIT NOVA is the language.
Host tools are bootstrap construction tools only.
Final target is self-hosting QBIT NOVA.

## Pipeline

QBIT NOVA source
Tokenizer
Parser
AST
IR
QVM
QBC
QBC Runner

## Runner Goal

Read QBC bytecode:

opcode
arg indexes
arg pool

Then decode into:

operation
arguments
safe state
safe trace
output

## QBC Runner v0.1 Mode

SAFE BYTECODE SIMULATION only.

No real OS changes.
No delete action.
No dangerous execution.
No fake quantum claim.

## State

QBC Runner tracks:

meta
laws
qbits
guards
actions
output

## Success Marker

QBIT_NOVA_QBC_RUNNER_V01
