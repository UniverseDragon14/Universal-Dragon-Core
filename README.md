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

[![NOVA QBIT Tests](https://github.com/UniverseDragon14/Universal-Dragon-Core/actions/workflows/qbit-tests.yml/badge.svg?branch=nova-v1.3.5-dev)](https://github.com/UniverseDragon14/Universal-Dragon-Core/actions/workflows/qbit-tests.yml)

NOVA QBIT is now tested automatically with GitHub Actions.

Current verified QBIT features:

- Single qbit gates: H, X, Z
- State and probability display
- Measurement collapse
- Multi-qbit register
- CNOT gate
- Bell-style linked state
- 20-run Bell repeat stability test
- Automated CI testing on `nova-v1.3.5-dev`

Latest locked milestone:

`NOVA QBIT v2 has passed automated GitHub CI testing.`

<!-- NOVA_QBIT_STATUS_END -->
