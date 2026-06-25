# QBIT NOVA Current Pointer v0.7.0

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

QBIT NOVA v0.7.0 Safe File Writer / Project Generator is GREEN.

## Accepted Proof

QBIT NOVA Safe File Writer v0.7:

qbit-nova-v1.4.0-dev-safe-file-writer-v07-green

## Current Safe Writer Meaning

The safe writer can generate files only under:

.tmp/qbit-generated-v07/

It must block:

- absolute paths
- parent traversal
- .env
- secret
- token
- key
- credential
- delete
- remove
- rmdir

## Current Safety Meaning

Every file writer result must keep:

- safe_stage: true
- os_execution: false
- delete_action: false

Writing requires approval=True.

Without approval, write_file must return needs_approval and must not write.

## Current Commands

Run safe writer proof:

./tools/qnova run examples/v2/safe_file_writer_v07.qn

Run install manifest:

./tools/qnova manifest examples/v2/qbit_nova_install_v03.qn

Run safe writer plan:

python3 tools/qbit_nova_safe_file_writer_v07.py plan

Run safe writer demo:

python3 tools/qbit_nova_safe_file_writer_v07.py demo

## Current Safe Pipeline

source.qn
qnova run / qnova manifest
guard approval engine
safe file writer
write only inside .tmp/qbit-generated-v07
verify no sensitive filenames
verify no FF opcode
verify no OS execution
verify no delete action

## Next Big Step

QBIT NOVA UI Manifest Builder v0.8.0

Goal:

Create a QBIT NOVA UI manifest format that can describe a simple UI safely.

This will prepare the path for NovaKutty UI generation from .qn later.

This must not edit the existing NovaKutty UI yet.

This must not touch business/dashboard/EVE.

This must not read secrets.

This must not delete files.

## Success Marker

QBIT_NOVA_CURRENT_POINTER_V070
