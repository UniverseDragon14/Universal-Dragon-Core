# NOVA to Node WhatsApp Adapter v1

## Purpose

This adapter defines how Node.js WhatsApp bridge reads NOVA/QBIT decision output and executes only approved safe actions.

## Principle

NOVA/QBIT decides.
Node.js executes.
Node.js must not invent the decision.

## Allowed NOVA Outputs

- CALL_SAFE_REPLY
- OWNER_APPROVAL_REQUIRED
- TEXT_REPLY
- VOICE_REPLY

## Node Execution Rules

### CALL_SAFE_REPLY

Node may:
- send a text reply to caller/message sender
- send a prepared voice note if available
- notify Aslam/owner

Node must not:
- auto-answer live call
- auto-call anyone

### OWNER_APPROVAL_REQUIRED

Node must:
- notify Aslam
- wait for owner approval

Node must not:
- send voice/call action automatically

## Safety

The adapter must not expose terminal commands through WhatsApp.

Universal Dragon Aslam continues.
