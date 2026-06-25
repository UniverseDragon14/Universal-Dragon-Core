# QBIT NOVA QN Manifest Runner v0.3

Creator: Aslam
Project: Universal Dragon
Brain: NovaKutty
Team: Askutty
Language: QBIT NOVA

## Purpose

This locks QBIT NOVA .QN Manifest Runner v0.3.

A `.qn` file can now behave like a safe manifest file.

Examples:

install.qn
hello.qn
mission.qn

## Manifest Meaning

A QBIT NOVA manifest may contain:

intent
target
package
output marker

## Safe Stage

At v0.3, manifest runner reads and verifies manifest meaning only.

It must not directly execute OS install actions.

It must not delete files.

It must not mix app/business/dashboard missions into this QBIT core chat.

## Pipeline

source.qn
qnova manifest
QBC file runner
write .qbc
load .qbc
decode safe trace
extract qbit manifest fields
verify output marker

## Current Command Shape

python3 tools/qbit_nova_qn_manifest_runner_v03.py source.qn output.qbc

Future command shape:

./tools/qnova manifest source.qn

## Success Marker

QBIT_NOVA_QN_MANIFEST_RUNNER_V03
