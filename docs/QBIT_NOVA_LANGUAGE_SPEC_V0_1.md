# QBIT NOVA Language Specification v0.1

QBIT NOVA is the main Universal Dragon language.

UD means Universal Dragon.

Creator: Aslam.

The user writes `.ud` files only.

Other technologies can exist inside the hidden runtime, compiler, or adapter layer, but they are not the public language identity.

## Core Identity

- Language name: QBIT NOVA
- Source extension: `.ud`
- UD meaning: Universal Dragon
- Creator: Aslam
- Project identity: Universal Dragon
- Brain identity: Askutty / NOVA

## Core Rule

User writes QBIT NOVA only.

Example:

```ud
nova universal_dragon
creator aslam
brain askutty

say "Universal Dragon online"

qbit dragon = |0>
h dragon
measure dragon

web screen:
  title "Universal Dragon"

native core:
  mode fast_runtime

guard:
  owner_approval required
  dangerous_action deny
