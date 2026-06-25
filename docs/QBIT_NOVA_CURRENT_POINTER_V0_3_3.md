# QBIT NOVA Current Pointer v0.3.3

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

QBIT NOVA v0.3 .qn manifest command is GREEN.

## Accepted Proofs

QN Source Spec v0.3:

qbit-nova-v1.4.0-dev-qn-source-spec-v03-green

Generic QN Runner v0.3 fix1:

qbit-nova-v1.4.0-dev-qnova-generic-runner-v03-fix1-green

QN Manifest Runner v0.3:

qbit-nova-v1.4.0-dev-qn-manifest-runner-v03-green

QNOVA Manifest Command v0.3:

qbit-nova-v1.4.0-dev-qnova-manifest-command-v03-green

## Current Commands

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
qnova manifest
write .qbc
load .qbc
decode safe trace
extract manifest fields
verify no FF opcode
verify no OS execution
verify no delete action

## Next Step

QBIT NOVA .QN Manifest Command Polish v0.3.1

Goal:

Improve qnova user command behavior:

- Better help text
- Better manifest output summary
- Keep qnova run working
- Keep qnova manifest working
- No OS install execution
- No delete action
- No secret reading

## Success Marker

QBIT_NOVA_CURRENT_POINTER_V033
