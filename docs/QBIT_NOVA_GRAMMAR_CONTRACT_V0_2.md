# QBIT NOVA Grammar Contract v0.2

QBIT NOVA is the Universal Dragon language direction.

UD means Universal Dragon.

Creator: Aslam
Team: Askutty
Brain: NovaKutty
Source extension: .ud

## Current Official Syntax

Example QBIT NOVA source:

    nova universal_dragon
    creator aslam
    team askutty
    brain novakutty

    say "QBIT NOVA language online"

    qbit dragon = |0>
    h dragon
    measure dragon

    screen main:
      title "Universal Dragon"

    guard:
      owner_approval required
      dangerous_action deny

## Grammar Blocks

### Identity

    nova <project_name>
    creator <creator_name>
    team <team_name>
    brain <brain_name>

### Output

    say "message"

### Qbit

    qbit <name> = |0>
    h <name>
    measure <name>

### Screen

    screen <name>:
      title "text"

### Guard

    guard:
      owner_approval required
      dangerous_action deny

## Safety Contract

QBIT NOVA must never allow destructive, dangerous, credential, or external adapter actions without explicit owner approval.

## v0.2 Scope

This version proves:

- .ud file recognition
- Universal Dragon identity
- Aslam creator identity
- Askutty team identity
- NovaKutty brain identity
- qbit creation
- H gate
- measurement
- screen title output
- guard output
- automated CI contract test
