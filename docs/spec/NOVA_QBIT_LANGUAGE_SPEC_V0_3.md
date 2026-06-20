# NOVA/QBIT Language Specification v0.3

## Project

Universal Dragon / NOVA / QBIT Language

## Creator

Aslam / Universal Dragon

## Version

v0.3-contract

## Purpose

NOVA/QBIT is a custom decision-language layer for safe AI and system workflows.

The language is designed to:

- declare a brain identity
- lock intent
- create qbit decision registers
- simulate possible outcomes
- observe selected state
- guard allowed or blocked outputs
- patch project files safely
- produce machine-readable adapter contracts

## Core Keywords

### brain

Declares the active NOVA brain/project identity.

Example:

brain universal_dragon

### intent

Locks the purpose of the current run.

Example:

intent "produce safe adapter contract"

### qbit

Creates a decision register.

Example:

qbit adapter_mode = |0>

### simulate

Maps qbit states to possible meanings.

Example:

simulate adapter_mode {
  when 0 => "safe action"
  when 1 => "blocked action"
}

### prob

Shows probability/state information.

Example:

prob adapter_mode

### observe

Observes the qbit state.

Example:

observe adapter_mode

### guard

Emits safe output only when matching the observed state.

Example:

guard adapter_mode {
  when 0 => say "NODE_ALLOWED:YES"
  when 1 => say "NODE_ALLOWED:NO"
}

### patch

Safely updates project files using approved replace syntax.

Example:

patch "file.txt" {
  replace "old" => "new"
}

## Adapter Contract Output

NOVA/QBIT can produce machine-readable output for external systems.

Current contract fields:

- NODE_CONTRACT
- NODE_CHANNEL
- NODE_ACTION
- NODE_APPROVAL
- NODE_RISK
- NODE_RUNTIME
- NODE_ALLOWED
- NODE_REASON

Example output:

NODE_CONTRACT:UNIVERSAL_ADAPTER
NODE_CHANNEL:ANY_SAFE_ADAPTER
NODE_ACTION:SAFE_EXECUTION_ALLOWED
NODE_APPROVAL:NO
NODE_RISK:LOW
NODE_RUNTIME:TEXT_UI_API_ONLY
NODE_ALLOWED:YES
NODE_REASON:NOVA permits only safe adapter execution

## Safety Rules

Allowed:

- text output
- UI output
- API adapter output
- owner notification
- safe patch operation inside project root
- owner approval flow

Blocked:

- raw terminal execution through adapters
- automatic live call answering
- automatic outbound call without approval
- unsafe system mutation without approval
- hidden destructive actions

## Current Proof Examples

- examples/v2/whatsapp_node_adapter_output_v1.nova
- examples/v2/whatsapp_adapter_contract_v2.nova
- examples/v2/whatsapp_adapter_contract_v3.nova
- examples/v2/universal_adapter_contract_v1.nova

## Current Tags

- nova-qbit-whatsapp-adapter-v1
- nova-qbit-whatsapp-contract-v2
- nova-qbit-whatsapp-contract-v3
- nova-qbit-universal-adapter-v1

## Status

This is an experimental language specification.

The language has working parser/runtime examples and adapter contract proofs.

Pending:

- formal grammar file
- adapter contract test file
- README language section
- public documentation page update
