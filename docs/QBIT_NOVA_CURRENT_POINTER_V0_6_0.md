# QBIT NOVA Current Pointer v0.6.0

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

QBIT NOVA v0.6.0 Guard / Approval Engine is GREEN.

## Accepted Proof

QBIT NOVA Guard / Approval Engine v0.6:

qbit-nova-v1.4.0-dev-guard-approval-engine-v06-green

## Current Guard Decisions

Allowed:

- check
- backup
- validate
- rollback
- learn
- emit

Needs human approval:

- install
- write_file
- network

Blocked:

- delete
- remove
- rmdir
- secret
- token
- unknown action

## Current Safety Meaning

Every guard decision must return:

- action
- decision
- safe_stage: true
- os_execution: false
- delete_action: false
- reason

## Current Commands

Run guard proof:

./tools/qnova run examples/v2/guard_approval_v06.qn

Read install manifest:

./tools/qnova manifest examples/v2/qbit_nova_install_v03.qn

Check guard engine:

python3 tools/qbit_nova_guard_approval_v06.py

## Next Big Step

QBIT NOVA Safe File Writer / Project Generator v0.7.0

Goal:

Create a guarded file writer that can only write safe generated files after guard approval.

This must not delete files.

This must not read secrets.

This must not execute OS install actions yet.

## Success Marker

QBIT_NOVA_CURRENT_POINTER_V060
