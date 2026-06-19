# Universal Dragon Device Sync Workflow v1

**Main project:** Universal Dragon Core  
**Branch:** nova-v1.3.5-dev  

## Devices

- Huawei Termux: outside/mobile development
- Raspberry Pi 5: room/server development
- GitHub: sync bridge and source of truth

## Rule

Do not manually copy project files between devices unless it is an emergency.

Use GitHub sync:

1. Before starting work:
   git pull --ff-only

2. After finishing work:
   git add .
   git commit -m "message"
   git push origin nova-v1.3.5-dev

3. On the other device:
   git pull --ff-only

## Workflow

Outside mode:
Huawei Termux -> work -> commit -> push

Room mode:
Pi5 -> pull -> continue -> commit -> push

## Purpose

This keeps Huawei Termux and Raspberry Pi 5 connected safely without duplicate files or version confusion.

Universal Dragon Aslam continues.
