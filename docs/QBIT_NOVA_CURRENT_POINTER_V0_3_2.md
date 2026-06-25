# QBIT NOVA Current Pointer v0.3.2

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

QBIT NOVA v0.3 source and bytecode loop is GREEN.

## Accepted Proofs

QBC File Writer v0.3 fix1:

qbit-nova-v1.4.0-dev-qbc-file-writer-v03-fix1-green

QBC File Loader v0.3:

qbit-nova-v1.4.0-dev-qbc-file-loader-v03-green

QBC File Runner v0.3:

qbit-nova-v1.4.0-dev-qbc-file-runner-v03-green

QNOVA Run Command v0.3:

qbit-nova-v1.4.0-dev-qnova-run-command-v03-green

Generic QN Runner fix1:

qbit-nova-v1.4.0-dev-qnova-generic-runner-v03-fix1-green

QN Source Spec v0.3:

qbit-nova-v1.4.0-dev-qn-source-spec-v03-green

## Current Meaning

.qn is short QBIT NOVA source.

.qnova is long QBIT NOVA source.

.qbc is QBIT NOVA compiled bytecode.

Python is bootstrap construction tool only.

## Current Command

./tools/qnova run examples/v2/qbit_nova_install_v03.qn

## Current Safe Pipeline

source.qn / source.qnova
qnova run
write .qbc
load .qbc
decode safe trace
verify output

## Next Step

QBIT NOVA .QN Manifest Runner v0.3

Goal:

Make `.qn` files act like safe manifest files.

Examples:

install.qn
hello.qn
mission.qn

The manifest runner must read intent, target, package, and output markers safely.

At this stage, manifest runner must not directly execute OS install actions.

## Success Marker

QBIT_NOVA_CURRENT_POINTER_V032
