# QBIT NOVA qnova manifest command v0.3

Creator: Aslam
Project: Universal Dragon
Brain: NovaKutty
Team: Askutty
Language: QBIT NOVA

## Purpose

This locks the user-facing QBIT NOVA qnova manifest command.

The command runs QBIT NOVA manifest sources through the existing safe manifest runner:

./tools/qnova manifest source.qn

It accepts:

.qn
.qnova
.ud

## Default Output

When no output path is supplied, qnova manifest writes QBC under:

.tmp/qnova-manifest-v03/<source_stem>.qbc

Example:

./tools/qnova manifest examples/v2/qbit_nova_install_v03.qn

Default QBC output:

.tmp/qnova-manifest-v03/qbit_nova_install_v03.qbc

## Pipeline

source.qn
qnova manifest
QBIT_NOVA_QN_MANIFEST_RUNNER_V03
SAFE_QN_MANIFEST_READ
QBC file runner
write .qbc
load .qbc
decode safe trace
extract manifest fields
verify output marker

## Safety

Manifest command v0.3 is a safe read and verification command only.

Manifest mode remains SAFE_QN_MANIFEST_READ.

It must not directly execute OS install actions.

It must not delete files.

It must not read secrets.

Generated QBC must not contain FF opcode.

## Success Markers

QBIT_NOVA_QNOVA_MANIFEST_COMMAND_V03

QBIT_NOVA_QNOVA_MANIFEST_COMMAND_V03_GREEN
