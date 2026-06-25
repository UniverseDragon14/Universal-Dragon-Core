# QBIT NOVA Current Pointer v0.5.0

Creator: Aslam
Project: Universal Dragon
Brain: NovaKutty
Team: Askutty

## Current Chat Scope

This chat is for QBIT NOVA language/core only.

Other app/business/dashboard missions must stay in separate chats.

## Current Clean Lab

Pi5 clean QBIT lab:

~/qbit-nova-labs/Universal-Dragon-Core-v02

Do not use old mixed folder for clean QBIT builds:

~/ud-github-sync

## Current Status

QBIT NOVA v0.5.0 Core Action Library is GREEN.

## Accepted Proof

QBIT NOVA Core Action Library v0.5:

qbit-nova-v1.4.0-dev-core-action-library-v05-green

## Current Safe Actions

The QBIT NOVA core safe action library now defines:

- check
- backup
- validate
- rollback
- learn
- emit

## Current Safety Meaning

Each core action must remain safe:

- safe_stage: true
- os_execution: false
- delete_action: false

Unknown actions must not silently pass.

Unknown actions must return safe error metadata.

## Current Commands

Help:

./tools/qnova help

Version:

./tools/qnova version

Run QBIT source:

./tools/qnova run examples/v2/core_actions_v05.qn

Read QBIT manifest:

./tools/qnova manifest examples/v2/qbit_nova_install_v03.qn

## Current Safe Pipeline

source.qn
qnova run / qnova manifest
write .qbc
load .qbc
decode safe trace
verify action meaning
verify no FF opcode
verify no OS execution
verify no delete action

## Next Big Step

QBIT NOVA Guard / Approval Engine v0.6.0

Goal:

Create a safe approval layer that can decide whether an action is allowed, blocked, or needs human approval.

This must not execute real OS install actions yet.

## Success Marker

QBIT_NOVA_CURRENT_POINTER_V050
