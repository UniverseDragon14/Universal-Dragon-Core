# QBIT NOVA Parser v0.1

Creator: Aslam
Project: Universal Dragon
Brain: NovaKutty
Language: QBIT NOVA

## Purpose

This is the first QBIT NOVA parser contract.

The tokenizer converts QBIT NOVA source into tokens.
The parser converts QBIT NOVA tokens into AST structure.

Existing host tools are bootstrap construction tools only.
They are not the public identity of QBIT NOVA.

## Parser Goal

Turn this:

guard intent:
    check first
    backup before_change
    validate after_change
    rollback on_fail
    learn always

Into a structured QBIT NOVA AST block.

## AST Types

- Program
- Statement
- HeaderStatement
- LawStatement
- QbitStatement
- EmitStatement
- GuardBlock

## DNA Rule

QBIT NOVA must grow toward:

tokenizer
parser
AST
IR
QVM
bytecode
compiler
self-hosting compiler

## Success Marker

QBIT_NOVA_PARSER_V01
