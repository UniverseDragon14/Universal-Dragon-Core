# QBIT NOVA Syntax v0.2

Creator: Aslam
Project: Universal Dragon
Brain: NovaKutty
Team: Askutty
Language: QBIT NOVA

## Purpose

This document locks QBIT NOVA symbolic syntax v0.2.

The goal is to make QBIT NOVA smaller, faster to type, easier for mobile keyboard, and closer to compact processor-style meaning.

## Truth Lock

QBIT NOVA is the language.
Host tools are bootstrap construction tools only.
Final target is self-hosting QBIT NOVA.

## Symbol Rules

@ = identity / header / law
q = qbit meaning
g = guard block
? = check
+ = safe action
! = fail / rollback safety
> = output
. = compact link

## Example

@nova.v02
@brain.novakutty
@creator.aslam
@project.universal_dragon
@team.askutty
@law.qbit_nova_identity_only
@law.bootstrap_tool_only

q.intent.safe_patch

g.intent:
? check.first
+ backup.before_change
+ validate.after_change
! rollback.on_fail
+ learn.always

> QBIT_NOVA_SYNTAX_V02

## Expanded Meaning

q.intent.safe_patch

means:

qbit intent = safe_patch

g.intent:
? check.first

means:

guard intent:
    check first

## Pipeline

Symbolic QBIT NOVA v0.2 source
Syntax translator
Tokenizer
Parser
AST
IR
QVM
QBC
QBC Runner
Full Runner

## Safety Law

No destructive execution.
No delete-first action.
No fake quantum claim.
No secret exposure.
Bootstrap tools are construction tools only.

## Success Marker

QBIT_NOVA_SYNTAX_V02
