# QBIT NOVA QBC v0.1

Creator: Aslam
Project: Universal Dragon
Brain: NovaKutty
Team: Askutty
Language: QBIT NOVA

## Purpose

This document locks the first QBIT NOVA bytecode contract.

QBC means QBIT Bytecode.

QBC converts QIR instructions into compact low-load instruction codes.

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
CPU bridge
future QPU adapter

## QBC Goal

Make instructions smaller and faster to load.

Readable IR:

ACTION.CHECK first

Compact QBC:

31 01

## QBC v0.1 Format

QBC v0.1 is a safe symbolic bytecode format.

Each instruction has:

opcode
arg indexes
source line
qpath

## Core Opcodes

01 PROGRAM.START
02 PROGRAM.END
10 META.SET
11 LAW.SET
20 QBIT.DEFINE
30 GUARD.START
31 ACTION.CHECK
32 ACTION.BACKUP
33 ACTION.VALIDATE
34 ACTION.ROLLBACK
35 ACTION.LEARN
36 GUARD.END
40 EMIT
FF UNKNOWN

## Safety Law

QBC v0.1 does not execute destructive system actions.
It only compacts QIR into bytecode proof.
No delete-first action.
No fake quantum claim.
No secret exposure.

## Success Marker

QBIT_NOVA_QBC_V01
