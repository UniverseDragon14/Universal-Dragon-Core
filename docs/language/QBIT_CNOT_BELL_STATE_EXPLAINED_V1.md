# QBIT CNOT Bell State Explained V1

Creator: Universal Dragon Aslam
System: Universal Dragon NOVA
Layer: QBIT symbolic quantum simulation

## Short Idea

This test proves that NOVA QBIT can simulate a simple two-qbit linked state.

The command sequence is:

qbit a = |0>
qbit b = |0>

h a
cnot a b

measure a
measure b

## Simple Meaning

Start:

a = 0
b = 0

Register:

|00> = 1.000

This means both qbits are fully zero.

## Step 1: Apply H Gate On a

Command:

h a

Result:

|00> = 0.707
|10> = 0.707

Meaning:

qbit a is now in 50/50 superposition.

b is still 0.

So the system is either:

a = 0, b = 0

or:

a = 1, b = 0

## Step 2: Apply CNOT a b

Command:

cnot a b

Meaning:

If control qbit a is 1, flip target qbit b.

If a is 0, leave b unchanged.

Before CNOT:

|00> = 0.707
|10> = 0.707

After CNOT:

|00> = 0.707
|11> = 0.707

## What Changed?

The |10> part became |11>.

That means when a becomes 1, b also becomes 1.

Now the two qbits are linked.

The system is now either:

a = 0, b = 0

or:

a = 1, b = 1

There should be no:

a = 0, b = 1

and no:

a = 1, b = 0

## Measurement Proof

When measuring:

measure a
measure b

The result should be one of these:

a = 0
b = 0

or:

a = 1
b = 1

Both results should match.

## Important Truth

This is not real quantum hardware.

This is a symbolic quantum simulator inside the NOVA language.

But the simulated math behavior follows the correct Bell-style idea:

H on first qbit + CNOT = linked two-qbit state.

## One Line Lock

H + CNOT creates a Bell-style linked state.

In NOVA QBIT:

|00> becomes a linked state of |00> and |11>.

## Why This Matters

This moves NOVA QBIT from single-qbit experiments into multi-qbit simulation.

NOVA QBIT now supports:

- multi-qbit register
- H gate
- X gate
- Z gate
- CNOT gate
- probability display
- measurement collapse
- Bell-style linked measurement

## Next Research Step

Run the Bell test many times and count the results.

Expected result:

00 appears many times
11 appears many times
01 should not appear
10 should not appear

That will prove linked measurement behavior more clearly.
