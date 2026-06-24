# QBIT NOVA Grammar Contract v0.3

QBIT NOVA is the Universal Dragon language direction.

UD means Universal Dragon.

Creator: Aslam
Team: Askutty
Brain: NovaKutty
Source extension: .ud

## v0.3 Goal

This version extends the v0.2 grammar with memory assignment, when blocks, and adapter blocks.

## Official v0.3 Syntax

    nova universal_dragon
    creator aslam
    team askutty
    brain novakutty

    let mission = "world record proof"

    qbit dragon = |0>
    h dragon
    measure dragon

    when dragon == 0:
      say "safe branch"

    when dragon == 1:
      say "owner approval branch"

    adapter whatsapp:
      mode safe_reply
      owner_approval required
      dangerous_action deny

## Grammar Additions

### Memory

    let <name> = "value"

### When block

    when <name> == <state>:
      say "message"

### Adapter block

    adapter <name>:
      mode <mode_name>
      owner_approval required
      dangerous_action deny

## Safety Contract

v0.3 does not execute external adapters. It only emits safe text output for proof and CI validation.

Dangerous runtime actions remain denied unless owner approval is explicit.
