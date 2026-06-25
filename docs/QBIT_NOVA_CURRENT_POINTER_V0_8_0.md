# QBIT NOVA Current Pointer v0.8.0

Creator: Aslam
Project: Universal Dragon
Brain: NovaKutty
Team: Askutty

## Current Chat Scope

This chat is for QBIT NOVA language/core only.

Business, WhatsApp, EVE, dashboard, customer quote, and app deployment missions must stay in separate chats unless they are explicitly being described as future QBIT outputs.

## Current Clean Lab

Pi5 clean QBIT lab:

~/qbit-nova-labs/Universal-Dragon-Core-v02

Do not use old mixed folder for clean QBIT builds:

~/ud-github-sync

## Current Status

QBIT NOVA v0.8.0 UI Manifest Builder is GREEN.

## Accepted Proof

QBIT NOVA UI Manifest Builder v0.8:

qbit-nova-v1.4.0-dev-ui-manifest-builder-v08-green

## Current UI Manifest Meaning

QBIT NOVA can now describe a safe UI manifest with:

- app_name
- title
- subtitle
- route
- theme
- components
- actions
- safety

Supported safe component types:

- hero
- text
- input
- button
- panel
- badge

Supported safe action types:

- ask
- navigate
- emit

## Current Safe Output Root

Generated demo UI manifests must stay under:

.tmp/qbit-generated-v08/

Generated files must not be committed.

## Current Safety Meaning

Every UI manifest builder result must keep:

- safe_stage: true
- os_execution: false
- delete_action: false

The builder must block:

- unknown component types
- unknown action types
- .env
- secret
- token
- key
- credential
- delete
- remove
- rmdir

## Current Commands

Run UI manifest proof:

./tools/qnova run examples/v2/ui_manifest_v08.qn

Run install manifest proof:

./tools/qnova manifest examples/v2/qbit_nova_install_v03.qn

Run UI manifest plan:

python3 tools/qbit_nova_ui_manifest_builder_v08.py plan

Run UI manifest demo:

python3 tools/qbit_nova_ui_manifest_builder_v08.py demo

## Current Safe Pipeline

source.qn
qnova run / qnova manifest
guard approval engine
safe file writer
UI manifest builder
write only inside .tmp/qbit-generated-v08
verify no sensitive filenames
verify no FF opcode
verify no OS execution
verify no delete action

## External Eve / WhatsApp Note

Universal Dragon Eve and WhatsApp bot are outside this chat scope.

They can later become downstream QBIT-generated apps.

Future QBIT rules should support:

- quote workflows
- image-required workflows
- validated source search workflows
- currency/country clarification
- no fake deep image analysis before image input exists

## Next Big Step

QBIT NOVA v0.9.0 = NovaKutty UI Manifest Project Generator

Goal:

Use the v0.8 UI manifest and v0.7 safe writer to generate a tiny safe UI project skeleton from QBIT metadata.

This must not edit the existing NovaKutty UI yet.

This must not touch business/dashboard/EVE.

This must not read secrets.

This must not delete files.

## Success Marker

QBIT_NOVA_CURRENT_POINTER_V080
