# QBIT NOVA QBC File Loader v0.3

Creator: Aslam
Project: Universal Dragon
Brain: NovaKutty
Team: Askutty
Language: QBIT NOVA

## Purpose

This locks QBIT NOVA v0.3 QBC file loading.

QBC File Writer v0.3 can write a real .qbc file.
QBC File Loader v0.3 can read that .qbc file, verify it, and safely decode it.

## Pipeline

.qnova source
Tokenizer
Parser
AST
IR
QBC
.qbc file
QBC File Loader
QBC Runner
Safe decoded trace

## Input Files

input.qbc
input.qbc.json
input.qbc.pool.json

## Mode

SAFE BYTECODE FILE LOAD only.

No OS action execution.
No delete action.
No fake quantum claim.
Bootstrap tools are construction tools only.

## Success Marker

QBIT_NOVA_QBC_FILE_LOADER_V03
