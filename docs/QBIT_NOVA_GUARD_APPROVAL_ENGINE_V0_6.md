# QBIT NOVA Guard / Approval Engine v0.6.0

Creator: Aslam
Project: Universal Dragon
Brain: NovaKutty
Team: Askutty
Language: QBIT NOVA

## Purpose

This locks QBIT NOVA Guard / Approval Engine v0.6.0.

The guard engine decides whether a QBIT NOVA action is allowed, blocked, or needs human approval.

This is a safety and approval layer only.

This is not OS execution.

This is not real install.

This is not delete.

Python remains bootstrap construction tooling only.

Project language: QBIT NOVA

## Core Dependency

The engine uses the existing safe QBIT NOVA core action library:

tools/qbit_nova_core_actions_v05.py

Allowed core actions come from that library.

## Guard Decisions

Known v0.6 guard decisions:

| Action | Decision | Reason |
| --- | --- | --- |
| check | allowed | Known safe QBIT NOVA core action from v0.5 library. |
| backup | allowed | Known safe QBIT NOVA core action from v0.5 library. |
| validate | allowed | Known safe QBIT NOVA core action from v0.5 library. |
| rollback | allowed | Known safe QBIT NOVA core action from v0.5 library. |
| learn | allowed | Known safe QBIT NOVA core action from v0.5 library. |
| emit | allowed | Known safe QBIT NOVA core action from v0.5 library. |
| install | needs_approval | Action can affect the environment and requires human approval. |
| write_file | needs_approval | Action can affect files and requires human approval. |
| network | needs_approval | Action can affect external systems and requires human approval. |
| delete | blocked | Destructive action is blocked by guard policy. |
| remove | blocked | Destructive action is blocked by guard policy. |
| rmdir | blocked | Destructive action is blocked by guard policy. |
| secret | blocked | Sensitive credential action is blocked by guard policy. |
| token | blocked | Sensitive credential action is blocked by guard policy. |
| unknown action | blocked | Unknown QBIT NOVA action is blocked by guard policy. |

## Decision Metadata

Every decision returns:

- action
- decision: allowed / needs_approval / blocked
- safe_stage: true
- os_execution: false
- delete_action: false
- reason

No unknown action should silently pass.

Unknown action handling must not execute anything.

Unknown action handling must return decision: blocked.

## Safe Command Proof

The source proof is:

examples/v2/guard_approval_v06.qn

It must run through:

./tools/qnova run examples/v2/guard_approval_v06.qn

Expected output marker:

QBIT_NOVA_GUARD_APPROVAL_ENGINE_V06

## Safety

No OS action execution.

No real install execution.

No delete action.

No secret reading.

No business, EVE, dashboard, Cloudflare, old sync, tokens, or .env scope.

Generated QBC must not contain standalone FF opcode.

## Success Marker

QBIT_NOVA_GUARD_APPROVAL_ENGINE_V06
