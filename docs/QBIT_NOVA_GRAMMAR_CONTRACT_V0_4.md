# QBIT NOVA Grammar Contract v0.4

QBIT NOVA is the Universal Dragon language direction.

UD means Universal Dragon.

Creator: Aslam
Team: Askutty
Brain: NovaKutty
Source extension: .ud

## v0.4 Goal

This version adds real conditional execution for measured qbits.

v0.3 only proved when blocks by loading both branches.
v0.4 selects only the branch that matches the measured qbit result.

## Runtime Rule

If measurement returns:

    measure dragon => 0

Only this branch executes:

    when dragon == 0:
      say "safe branch selected"

If measurement returns:

    measure dragon => 1

Only this branch executes:

    when dragon == 1:
      say "owner approval branch selected"

No external adapter action is executed.
