# NOVA LINK / DRAGON GATE - Master Key Remote Control Plan

Creator: Aslam
Purpose: Control only Aslam-owned devices safely from Termux, even when IP changes.

## Core Problem
IP is only a door number. It changes with WiFi, mobile data, VPN, office network, room WiFi, router changes, and travel.

## Solution
Use identity-based control:
- Aslam phone keeps master key
- Pi5/laptop stores trusted device key or verifier
- Every command is signed
- Device verifies signature before action
- Relay only passes messages
- Risky actions require approval
- All commands are logged
- Backups before changes

## Components
1. novalink
   Mobile Termux commander.

2. novad
   Device agent running on Pi5/laptop.

3. dragon-relay
   Stable meeting point for devices when IP changes.

## Safe Rules
- Only Aslam-owned enrolled devices
- No password-based public control
- No destructive command without approval
- No exposing Pi5 internal ports directly
- Port 5000 remains protected NOVA backend
- Full logs and rollback

## Port Map
5000 = NOVA backend / protected
5058 = EVE Fire UI
5062 = Studio
8090 = extra local portal

## First Build
Start with local signed command files.
Then add Pi5 agent.
Then add relay mode.
