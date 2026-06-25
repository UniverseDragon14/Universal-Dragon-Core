# QBIT NOVA QN Source Spec v0.3

Creator: Aslam
Project: Universal Dragon
Brain: NovaKutty
Team: Askutty
Language: QBIT NOVA

## Purpose

This locks the source file meaning for QBIT NOVA v0.3.

## Source Extensions

### .qn

`.qn` is the short QBIT NOVA source file extension.

Use `.qn` for normal compact source files.

Example:

install.qn
hello.qn
mission.qn

### .qnova

`.qnova` is the long QBIT NOVA source file extension.

Use `.qnova` for formal examples, docs, lab files, or long-form source files.

Example:

qbit_nova_qbc_file_runner_v03.qnova

### .qbc

`.qbc` is QBIT NOVA compiled bytecode.

It is generated from `.qn` or `.qnova`.

Example:

install.qn
  ↓
install.qbc

## Install Meaning

install.qn means:

A QBIT NOVA install intent or install manifest.

At v0.3, install.qn is safe manifest only.

It must not directly execute OS installation.

It can be compiled to .qbc, loaded, decoded, and verified safely.

## Python Meaning

Python files are bootstrap construction tools only.

Python is not the project identity.

Project language: QBIT NOVA
Short source: .qn
Long source: .qnova
Bytecode: .qbc
Bootstrap tool: Python

## Current User Command

Run QBIT NOVA source using:

./tools/qnova run source.qn

or:

./tools/qnova run source.qnova

## Current Safe Pipeline

source.qn / source.qnova
qnova run
QBC File Runner
write .qbc
load .qbc
decode safe trace
verify output

## Safety Rules

No OS action execution.
No delete action.
No fake quantum claim.
No business/dashboard mixing in this chat.
Bootstrap tools are construction tools only.

## Success Marker

QBIT_NOVA_QN_SOURCE_SPEC_V03
