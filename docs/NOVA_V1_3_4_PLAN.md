# NOVA v1.3.4 Development Plan

Base stable release:
- Tag: nova-v1.3.3
- Commit: e4914c5
- Status: GREEN

## Goal

Make NOVA easier to use from mobile Termux.

## Planned upgrades

1. Clean help menu
2. `nova notes` command to view latest saved notes
3. `nova router` command improved
4. `nova adapter` report included in doctor flow
5. Package repo polish
6. Safer version labels
7. No breaking change to v1.3.3 stable package

## Current engines

- nova core
- qbit
- python
- bash
- node
- sqlite
- adapter checker

## Rule

Do not overwrite stable v1.3.3.
All new work goes into v1.3.4-dev first.
