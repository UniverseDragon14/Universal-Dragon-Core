# NOVA/QBIT Grammar v0.3

## Project

Universal Dragon / NOVA / QBIT Language

## Version

v0.3-contract

## Grammar Style

This grammar describes the current NOVA/QBIT v2 language shape.

It is written as a practical EBNF-style grammar, not final compiler theory grammar.

## Program

program =
  statement*

statement =
  brain_statement
  | intent_statement
  | qbit_statement
  | gate_statement
  | simulate_block
  | prob_statement
  | observe_statement
  | guard_block
  | patch_block
  | say_statement

## Brain Statement

brain_statement =
  "brain" identifier

Example:

brain universal_dragon

## Intent Statement

intent_statement =
  "intent" string

Example:

intent "produce safe adapter contract"

## Qbit Statement

qbit_statement =
  "qbit" identifier "=" qbit_state

qbit_state =
  "|0>"
  | "|1>"

Example:

qbit adapter_mode = |0>

## Gate Statement

gate_statement =
  gate_name identifier

gate_name =
  "h"
  | "x"
  | "z"

Examples:

h adapter_mode
x adapter_mode
z adapter_mode

## Simulate Block

simulate_block =
  "simulate" identifier "{" simulate_case* "}"

simulate_case =
  "when" state_value "=>" string

state_value =
  "0"
  | "1"

Example:

simulate adapter_mode {
  when 0 => "safe action"
  when 1 => "blocked action"
}

## Probability Statement

prob_statement =
  "prob" identifier

Example:

prob adapter_mode

## Observe Statement

observe_statement =
  "observe" identifier

Example:

observe adapter_mode

## Guard Block

guard_block =
  "guard" identifier "{" guard_case* "}"

guard_case =
  "when" state_value "=>" guard_action

guard_action =
  say_statement
  | rollback_statement

say_statement =
  "say" string

rollback_statement =
  "rollback"

Example:

guard adapter_mode {
  when 0 => say "NODE_ALLOWED:YES"
  when 1 => say "NODE_ALLOWED:NO"
}

## Patch Block

patch_block =
  "patch" string "{" patch_operation* "}"

patch_operation =
  "replace" string "=>" string

Example:

patch "file.txt" {
  replace "old" => "new"
}

## Adapter Contract Output

adapter_output =
  "NODE_CONTRACT:" value
  | "NODE_CHANNEL:" value
  | "NODE_ACTION:" value
  | "NODE_APPROVAL:" value
  | "NODE_RISK:" value
  | "NODE_RUNTIME:" value
  | "NODE_ALLOWED:" value
  | "NODE_REASON:" value

value =
  string_without_newline

## Identifiers

identifier =
  letter (letter | digit | "_" | "-")*

## Strings

string =
  double_quote character* double_quote

## Current Known Keywords

- brain
- intent
- qbit
- h
- x
- z
- simulate
- when
- prob
- observe
- guard
- say
- rollback
- patch
- replace

## Safety Grammar Rule

The grammar allows guarded output.

It does not define direct raw terminal execution.

External runtime execution must happen only through adapter contract fields.

## Status

This grammar matches the current v0.3-contract language direction.

Pending future grammar:

- multi-qbit adapter states
- typed variables
- structured JSON output
- approval block syntax
- memory block syntax
- module import syntax
