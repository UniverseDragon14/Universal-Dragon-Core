# QBIT NOVA AST v0.1

Creator: Aslam
Project: Universal Dragon
Brain: NovaKutty
Team: Askutty
Language: QBIT NOVA

## Purpose

This document locks the first QBIT NOVA AST contract.

AST means Abstract Syntax Tree.

Tokenizer reads symbols.
Parser builds structure.
AST becomes the official QBIT NOVA brain skeleton.

## Truth Lock

QBIT NOVA is the language.
Host tools are bootstrap construction tools only.
Final target is self-hosting QBIT NOVA.

## AST Goal

Convert QBIT NOVA source into a stable tree that can later be converted into:

IR
QVM instructions
QBIT bytecode
CPU execution
future QPU adapter

## AST Node Types

- QASTProgram
- QASTHeader
- QASTLaw
- QASTQbit
- QASTGuard
- QASTAction
- QASTEmit
- QASTStatement

## AST Node Fields

Each node should contain:

id
type
line
head
values
children
qpath

## Example

Source:

guard intent:
    check first
    backup before_change
    validate after_change
    rollback on_fail
    learn always

AST:

QASTGuard
  QASTAction check.first
  QASTAction backup.before_change
  QASTAction validate.after_change
  QASTAction rollback.on_fail
  QASTAction learn.always

## Success Marker

QBIT_NOVA_AST_V01
