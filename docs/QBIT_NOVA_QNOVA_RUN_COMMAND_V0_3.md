# QBIT NOVA qnova run command v0.3

Creator: Aslam
Project: Universal Dragon
Brain: NovaKutty
Team: Askutty
Language: QBIT NOVA

## Purpose

This locks a user-facing QBIT NOVA run command.

Before this, the full QBC loop was run through Python tool files directly.

Now the user can run the QBIT NOVA loop through:

./tools/qnova run source.qnova

## Important

Python is still used internally as a bootstrap construction tool.

Python is not the project identity.

Project language: QBIT NOVA
Bytecode: QBC
Runtime path: QVM / QBC Runner
Temporary builder: Python

## Pipeline

source.qnova
qnova run
QBC File Runner
write .qbc
load .qbc
decode safe trace
verify output

## Mode

SAFE QNOVA RUN COMMAND only.

No OS action execution.
No delete action.
No fake quantum claim.
Bootstrap tools are construction tools only.

## Success Marker

QBIT_NOVA_QNOVA_RUN_COMMAND_V03
