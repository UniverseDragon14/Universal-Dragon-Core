# QBIT NOVA Safe File Writer / Project Generator v0.7.0

Creator: Aslam
Project: Universal Dragon
Brain: NovaKutty
Team: Askutty
Language: QBIT NOVA

## Purpose

This locks QBIT NOVA Safe File Writer / Project Generator v0.7.0.

This is a safe generation layer only.

It can write approved text files only under:

.tmp/qbit-generated-v07/

It can generate one tiny sample QBIT NOVA project under:

.tmp/qbit-generated-v07/sample_qbit_project/

This is not OS execution.

This is not real install.

This is not delete.

Python remains bootstrap construction tooling only.

Project language: QBIT NOVA

## Guard Dependency

The writer uses the existing guard approval engine:

tools/qbit_nova_guard_approval_v06.py

The write action is:

write_file

The guard decision for write_file is:

decision: needs_approval

Unknown action handling must go through the guard engine and return decision: blocked.

## Safe Path Policy

Allowed output root:

.tmp/qbit-generated-v07/

Blocked paths:

- absolute paths
- parent traversal using ..
- directory-only paths
- sensitive names, including .env, secret, token, key, credential

Blocked actions:

- delete
- remove
- rmdir
- unknown action

## Approval Policy

Writing a file requires explicit approval=True.

If approval=False:

- decision: needs_approval
- written: false
- mode: SAFE_FILE_WRITE_METADATA_ONLY

If approval=True and the path is safe:

- decision: success
- written: true
- mode: SAFE_GENERATED_FILE_WRITE

## Required Metadata

Every result returns:

- marker: QBIT_NOVA_SAFE_FILE_WRITER_V07
- mode: SAFE_FILE_WRITE_METADATA_ONLY or SAFE_GENERATED_FILE_WRITE
- safe_stage: true
- os_execution: false
- delete_action: false
- approval_required: true / false
- written: true / false
- path
- reason

## Generated Project

The project generator writes only through the same safe writer function.

Generated files:

- README.md
- manifest.json
- src/main.qn

Generated root:

.tmp/qbit-generated-v07/sample_qbit_project/

Generated files must not be committed.

## Safe Command Proof

The source proof is:

examples/v2/safe_file_writer_v07.qn

It must run through:

./tools/qnova run examples/v2/safe_file_writer_v07.qn

Expected output marker:

QBIT_NOVA_SAFE_FILE_WRITER_V07

## Bootstrap Commands

Plan only:

python3 tools/qbit_nova_safe_file_writer_v07.py plan

Safe demo generation:

python3 tools/qbit_nova_safe_file_writer_v07.py demo

The demo may generate files only under:

.tmp/qbit-generated-v07/

## Safety

No OS action execution.

No real install execution.

No delete action.

No secret reading.

No business, EVE, dashboard, Cloudflare, old sync, tokens, or .env scope.

Generated QBC must not contain standalone FF opcode.

No generated file path outside .tmp/qbit-generated-v07/.

## Success Marker

QBIT_NOVA_SAFE_FILE_WRITER_V07
