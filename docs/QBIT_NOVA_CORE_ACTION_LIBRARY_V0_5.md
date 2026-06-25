# QBIT NOVA Core Action Library v0.5.0

Creator: Aslam
Project: Universal Dragon
Brain: NovaKutty
Team: Askutty
Language: QBIT NOVA

## Purpose

This locks QBIT NOVA Core Action Library v0.5.0.

The library defines safe QBIT NOVA meaning metadata for known core actions.

This is not OS execution.

This is not real install.

This is not delete.

Python remains bootstrap construction tooling only.

Project language: QBIT NOVA

## Core Actions

Known v0.5 core actions:

- check
- backup
- validate
- rollback
- learn
- emit

Each action exposes:

- name
- category
- safe_stage: true
- os_execution: false
- delete_action: false
- description

## Action Meaning

check means inspect or confirm QBIT NOVA state before continuing.

backup means preserve safe QBIT NOVA state before later stages.

validate means verify QBIT NOVA source, bytecode, manifest, or metadata meaning.

rollback means return to a safe prior QBIT NOVA state if validation fails.

learn means record safe language/core meaning for future QBIT NOVA reasoning.

emit means produce QBIT NOVA output text or markers.

## Unknown Action Rule

No unknown action should silently pass.

An unknown action must return safe error metadata.

Unknown action handling must not execute anything.

Unknown action handling must keep:

- safe_stage: true
- os_execution: false
- delete_action: false
- allowed: false

## Safe Command Proof

The source proof is:

examples/v2/core_actions_v05.qn

It must run through:

./tools/qnova run examples/v2/core_actions_v05.qn

Expected output marker:

QBIT_NOVA_CORE_ACTION_LIBRARY_V05

## Safety

No OS action execution.

No real install execution.

No delete action.

No secret reading.

No business, EVE, dashboard, Cloudflare, old sync, tokens, or .env scope.

Generated QBC must not contain FF opcode.

## Success Marker

QBIT_NOVA_CORE_ACTION_LIBRARY_V05
