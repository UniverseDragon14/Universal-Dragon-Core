# QBIT NOVA Current Pointer v0.4.0

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

QBIT NOVA v0.4.0 command polish is GREEN.

## Accepted Proof

QBIT NOVA qnova command polish v0.4:

qbit-nova-v1.4.0-dev-qnova-command-polish-v04-green

## Current Commands

Help:

./tools/qnova help

Version:

./tools/qnova version

Run QBIT source:

./tools/qnova run examples/v2/qbit_nova_install_v03.qn

Read QBIT manifest:

./tools/qnova manifest examples/v2/qbit_nova_install_v03.qn

## Current Meaning

.qn is short QBIT NOVA source.

.qnova is long QBIT NOVA source.

.qbc is QBIT NOVA compiled bytecode.

install.qn is a safe install manifest.

Python is bootstrap construction tool only.

## Current Safe Pipeline

source.qn
qnova run / qnova manifest
write .qbc
load .qbc
decode safe trace
extract manifest fields
verify no FF opcode
verify no OS execution
verify no delete action

## Completed v0.4.0 Behavior

- qnova help works
- qnova version works
- qnova run works
- qnova manifest works
- manifest summary works
- JSON output preserved
- no OS install execution
- no delete action
- no secret reading
- no standalone FF opcode

## Next Big Step

QBIT NOVA Core Action Library v0.5.0

Goal:

Create a stable action library for known safe QBIT actions:

check
backup
validate
rollback
learn
emit

This must stay safe and must not execute OS install actions yet.

## Success Marker

QBIT_NOVA_CURRENT_POINTER_V040
