# QBIT NOVA qnova command polish v0.4.0

Creator: Aslam
Project: Universal Dragon
Brain: NovaKutty
Team: Askutty
Language: QBIT NOVA

## Purpose

This locks QBIT NOVA qnova command polish v0.4.0.

The command remains a safe bootstrap command wrapper for QBIT NOVA language/core work only.

Python is still bootstrap construction tooling only.

Project language: QBIT NOVA

## Commands

Help command:

./tools/qnova help

Required help output:

QBIT NOVA command help
available commands: run, manifest, help, version
source extensions: .qn, .qnova, .ud
output extension: .qbc
safety note: no OS install, no delete, bootstrap only

Version command:

./tools/qnova version

Required version output:

QBIT_NOVA_QNOVA_COMMAND_POLISH_V04
Current stage: v0.4.0
Source: .qn / .qnova
Bytecode: .qbc
Mode: SAFE_BOOTSTRAP_COMMAND

## Existing Commands

These v0.3 commands must keep working:

./tools/qnova run examples/v2/qbit_nova_install_v03.qn

./tools/qnova manifest examples/v2/qbit_nova_install_v03.qn

## Manifest Summary

The manifest command keeps the v0.3 JSON output.

It also prints a compact summary:

QBIT_NOVA_QNOVA_MANIFEST_SUMMARY_V04
intent
target
package
output_marker
os_execution: false
delete_action: false

## Safety

Mode remains safe bootstrap command only.

No OS install execution.

No delete action.

No secret reading.

Generated QBC must not contain FF opcode.

Business, EVE, dashboard, Cloudflare, old ~/ud-github-sync, secrets, tokens, and .env are out of scope.

## Success Marker

QBIT_NOVA_QNOVA_COMMAND_POLISH_V04
