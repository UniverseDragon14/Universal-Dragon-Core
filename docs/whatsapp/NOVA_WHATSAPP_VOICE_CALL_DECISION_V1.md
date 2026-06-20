# NOVA WhatsApp Voice and Call Decision v1

## Purpose

This document defines how NOVA/QBIT decides WhatsApp voice reply and incoming call handling before Node execution.

## Rule

NOVA/QBIT is the decision brain.

Node.js is only the execution body.

## NOVA Decision File

Example:

`examples/v2/whatsapp_voice_call_decision_v1.nova`

## Decision Outputs

| NOVA Output | Meaning | Node Action |
|---|---|---|
| CALL_SAFE_REPLY | Incoming call must be handled safely | Send busy text/voice note and notify owner |
| OWNER_APPROVAL_REQUIRED | Voice/call action needs Aslam approval | Do not auto-call; wait for owner action |

## Safety

NOVA must not allow automatic live call answering without owner approval.

Allowed v1 actions:

- send text reply
- send busy reply
- notify owner
- prepare voice note reply

Blocked v1 actions:

- auto-answer live WhatsApp call
- auto-call without approval
- raw terminal execution through WhatsApp

## Architecture

WhatsApp event
→ Node bridge receives
→ NOVA/QBIT decision file runs
→ NOVA outputs decision
→ Node executes only allowed action

Universal Dragon Aslam continues.
