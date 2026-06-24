# QBIT NOVA Grammar Contract v0.5 AST

QBIT NOVA is the Universal Dragon language direction.

UD means Universal Dragon.

Creator: Aslam
Team: Askutty
Brain: NovaKutty
Source extension: .ud

## v0.5 Goal

This version adds AST export.

AST means Abstract Syntax Tree.

It converts a `.ud` source file into a structured JSON brain map.

## Why this matters

Before v0.5, QBIT NOVA could run `.ud` files.

From v0.5, QBIT NOVA can also understand the structure of `.ud` files.

This is needed for:

- editor support
- visual builder
- game logic
- safe adapters
- future compiler
- robot / EVE brain planning

## Command

    nova ast examples/v2/qbit_nova_v05_ast.ud

## Safety

AST export only reads `.ud` files.
It does not execute external adapters.
