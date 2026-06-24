# QBIT NOVA Language Specification v0.1

QBIT NOVA is a new Universal Dragon language.

UD means Universal Dragon.

Creator: Aslam.

The user writes `.ud` files only.

QBIT NOVA is not Python, not C, not C++, not Java, not HTML, and not TypeScript.

Other technologies may exist later only as hidden compiler or runtime targets. They are not the public language identity.

## Core Identity

- Language name: QBIT NOVA
- Source extension: `.ud`
- UD meaning: Universal Dragon
- Creator: Aslam
- Project identity: Universal Dragon
- Brain identity: Askutty / NOVA

## Core Syntax

    nova universal_dragon
    creator aslam
    brain askutty

    say "Universal Dragon online"

    qbit dragon = |0>
    h dragon
    measure dragon

    screen main:
      title "Universal Dragon"

    guard:
      owner_approval required
      dangerous_action deny

## Language Layers

1. QBIT NOVA source: `.ud`
2. QBIT engine: state, decision, guard, memory
3. Runtime targets: native, web, app, system, robot
4. Guard layer: safety and owner approval
5. Output layer: terminal, web, phone, robot, WhatsApp bridge

## Safety Rule

No delete, no attack, no credential access, and no external action without explicit owner approval.
