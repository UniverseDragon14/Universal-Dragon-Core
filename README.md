# Universal Dragon Core - NOVA

Creator: Aslam  
Core: NOVA  
Branch: Termux Mobile Field Lab  
Runtime: Python  

## Current Version

NOVA Python Core v1.3.1

## Features

- `.nova` file runner
- variables
- math calculation
- if/end blocks
- repeat/end loops
- define/call functions
- function arguments
- use/import library files
- doctor check
- manifest generation
- export/import preview
- Pi5 syncpack and synccheck

## Quick Test

```bash
nova version
nova doctor
nova synccheck

<!-- NOVA_QBIT_STATUS_START -->
## NOVA QBIT Test Status

[![NOVA QBIT Tests](https://github.com/UniverseDragon14/Universal-Dragon-Core/actions/workflows/qbit-tests.yml/badge.svg?branch=nova-v1.4.0-dev)](https://github.com/UniverseDragon14/Universal-Dragon-Core/actions/workflows/qbit-tests.yml)

NOVA QBIT is now tested automatically with GitHub Actions.

Current verified QBIT features:

- Single qbit gates: H, X, Z
- State and probability display
- Measurement collapse
- Multi-qbit register
- CNOT gate
- Bell-style linked state
- 20-run Bell repeat stability test
- Automated CI testing on `nova-v1.4.0-dev`

Latest locked milestone:

`NOVA QBIT v2 has passed automated GitHub CI testing.`

<!-- NOVA_QBIT_STATUS_END -->

---

# NOVA/QBIT Language

NOVA/QBIT is an experimental decision-language layer created under Universal Dragon by Aslam.

Current version: 0.3.0-contract

## Purpose

NOVA/QBIT separates decision logic from execution.

NOVA decides intent, qbit state, probability, observed state, guard result, and adapter contract output.

External adapters such as WhatsApp, web apps, APIs, or system bridges only obey the emitted contract.

## Core Keywords

brain, intent, qbit, simulate, prob, observe, guard, say, patch, replace

## Adapter Contract Fields

NODE_CONTRACT
NODE_CHANNEL
NODE_ACTION
NODE_APPROVAL
NODE_RISK
NODE_RUNTIME
NODE_ALLOWED
NODE_REASON

## Run Examples

python3 nova-lang/v2/nova2_run.py examples/v2/universal_adapter_contract_v1.nova
python3 nova-lang/v2/nova2_run.py examples/v2/whatsapp_adapter_contract_v3.nova

## Run Tests

python3 tests/nova_qbit_adapter_contracts_check.py

## Spec Files

docs/spec/NOVA_QBIT_LANGUAGE_SPEC_V0_3.md
docs/spec/NOVA_QBIT_GRAMMAR_V0_3.md

## Safety

NOVA/QBIT allows safe adapter output and owner approval flows.

It blocks raw terminal execution through external adapters and does not allow automatic live call answering or dangerous system mutation without approval.

---
