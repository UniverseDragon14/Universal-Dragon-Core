# QBIT NOVA UI Manifest Builder v0.8.0

Creator: Aslam
Project: Universal Dragon
Brain: NovaKutty
Team: Askutty
Language: QBIT NOVA

## Purpose

This locks QBIT NOVA UI Manifest Builder v0.8.0.

This is a safe UI manifest builder only.

It prepares a future path for NovaKutty UI generation from .qn, but this stage does not generate real app code and does not edit the existing NovaKutty UI.

Python remains bootstrap construction tooling only.

Project language: QBIT NOVA

## Safe Output Root

Generated demo files may be written only under:

.tmp/qbit-generated-v08/

Generated manifest:

.tmp/qbit-generated-v08/novakutty_ui_manifest/manifest.json

Optional generated README:

.tmp/qbit-generated-v08/novakutty_ui_manifest/README.md

Generated files must not be committed.

## Safety Dependencies

The builder uses the existing safe writer:

tools/qbit_nova_safe_file_writer_v07.py

The builder uses the existing guard approval engine where write approval metadata is needed:

tools/qbit_nova_guard_approval_v06.py

The write action is:

write_file

The guard decision for write_file is:

decision: needs_approval

The builder supplies explicit bootstrap approval only after manifest validation passes and only for the v0.8 safe output root.

## Manifest Fields

The safe UI manifest object must include:

- app_name
- title
- subtitle
- route
- theme
- components
- actions
- safety

The manifest metadata must include:

- marker: QBIT_NOVA_UI_MANIFEST_BUILDER_V08
- mode: SAFE_UI_MANIFEST_BUILDER
- safe_stage: true
- os_execution: false
- delete_action: false
- app_name
- generated_root
- manifest_path
- components_count
- actions_count
- output

## Component Policy

Allowed component types only:

- hero
- text
- input
- button
- panel
- badge

Unknown component types must return safe blocked metadata.

## Action Policy

Allowed action types only:

- ask
- navigate
- emit

Unknown action types must return safe blocked metadata.

## Sensitive Name Policy

Sensitive fields or names are blocked when they contain:

- .env
- secret
- token
- key
- credential

This policy applies before any generated write is attempted.

## Safe Command Proof

The source proof is:

examples/v2/ui_manifest_v08.qn

It must run through:

./tools/qnova run examples/v2/ui_manifest_v08.qn

Expected output marker:

QBIT_NOVA_UI_MANIFEST_BUILDER_V08

## Bootstrap Commands

Plan only:

python3 tools/qbit_nova_ui_manifest_builder_v08.py plan

Safe demo generation:

python3 tools/qbit_nova_ui_manifest_builder_v08.py demo

The demo may generate files only under:

.tmp/qbit-generated-v08/

## Safety

No OS action execution.

No install execution.

No delete action.

No secret reading.

No business, EVE, dashboard, Cloudflare, old sync, tokens, or .env scope.

No existing NovaKutty UI files are modified.

Generated QBC must not contain standalone FF opcode.

No generated file path outside .tmp/qbit-generated-v08/.

## Success Marker

QBIT_NOVA_UI_MANIFEST_BUILDER_V08
