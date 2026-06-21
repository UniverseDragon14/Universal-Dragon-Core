# Qbit Nova Game v1

Project: Universal Dragon Core / NOVA / QBIT
Creator: Aslam / Universal Dragon

## Purpose

Qbit Nova Game turns the existing NOVA/QBIT idea into a small browser game inside the dashboard.

The player controls Nova with short beginner commands. Each level teaches one programming idea before the next idea appears.

## Lessons

1. Wake Nova: direct commands such as `move right` and `activate core`.
2. Orb Loop: `repeat` blocks for clean repeated movement.
3. Qbit Gate: `h nova`, `prob nova`, `measure nova`, and `if nova == 1: move down`.

## Current UI File

`src/components/QbitNovaGame.tsx`

The game is mounted in:

`src/App.tsx`

## Commands Supported

```text
move up
move down
move left
move right
repeat 3 {
  move right
}
collect orb
activate gate
h nova
x nova
prob nova
measure nova
if nova == 1: move down
activate core
```

## Design Rule

This is a teaching game, not a raw system adapter. It only changes local browser game state.

## Next Upgrade Path

- add score stars
- add level save state
- add mobile touch controls
- connect later to `.nova` example missions
- add Tamil/Tanglish tutorial text mode
