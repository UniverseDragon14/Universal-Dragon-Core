# QBIT NOVA IR v0.1

Creator: Aslam
Project: Universal Dragon
Brain: NovaKutty
Team: Askutty
Language: QBIT NOVA

## Purpose

This document locks the first QBIT NOVA IR contract.

IR means Intermediate Representation.

Tokenizer reads symbols.
Parser builds structure.
AST builds brain skeleton.
IR converts the AST skeleton into execution-ready nerve signals.

## Truth Lock

QBIT NOVA is the language.
Host tools are bootstrap construction tools only.
Final target is self-hosting QBIT NOVA.

## IR Goal

Convert QAST nodes into stable QIR instructions that can later run through:

QVM
QBIT bytecode
CPU execution
future QPU adapter

## IR Instruction Fields

Each instruction should contain:

id
op
args
line
qpath

## Core IR Ops

- PROGRAM.START
- PROGRAM.END
- META.SET
- LAW.SET
- QBIT.DEFINE
- GUARD.START
- GUARD.END
- ACTION.CHECK
- ACTION.BACKUP
- ACTION.VALIDATE
- ACTION.ROLLBACK
- ACTION.LEARN
- EMIT

## Example

QBIT NOVA source:

qbit intent = safe_patch

guard intent:
    check first
    backup before_change
    validate after_change
    rollback on_fail
    learn always

IR output:

QBIT.DEFINE intent safe_patch
GUARD.START intent
ACTION.CHECK first
ACTION.BACKUP before_change
ACTION.VALIDATE after_change
ACTION.ROLLBACK on_fail
ACTION.LEARN always
GUARD.END intent

## Success Marker

QBIT_NOVA_IR_V01
