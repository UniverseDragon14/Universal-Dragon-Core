# NOVA/QBIT v0.3 Release Manifest

## Project

Universal Dragon / NOVA / QBIT Language

## Creator

Aslam / Universal Dragon

## Release Version

0.3.0-contract

## Release Type

Experimental language contract milestone

## Main Goal

This release turns NOVA/QBIT from working examples into a structured experimental language package with:

- language specification
- formal grammar
- version file
- adapter contract examples
- automated tests
- GitHub Actions CI
- README documentation
- tagged milestones

## Included Language Proofs

### WhatsApp Adapter Contract v3

File:

examples/v2/whatsapp_adapter_contract_v3.nova

Purpose:

Defines safe WhatsApp adapter output with approval, risk, runtime, allowed status, and reason.

Tag:

nova-qbit-whatsapp-contract-v3

### Universal Adapter Contract v1

File:

examples/v2/universal_adapter_contract_v1.nova

Purpose:

Defines safe adapter execution rules for any external adapter while blocking raw runtime execution.

Tag:

nova-qbit-universal-adapter-v1

## Specification Files

- docs/spec/NOVA_QBIT_LANGUAGE_SPEC_V0_3.md
- docs/spec/NOVA_QBIT_GRAMMAR_V0_3.md
- NOVA_QBIT_VERSION

## Tests

Test file:

tests/nova_qbit_adapter_contracts_check.py

Validated contracts:

- WhatsApp adapter contract v3
- Universal adapter contract v1

Tag:

nova-qbit-adapter-contract-tests-v0.3

## CI

GitHub Actions workflow now runs adapter contract tests.

Tag:

nova-qbit-adapter-contract-ci-v0.3

## README

README now includes NOVA/QBIT language overview, keywords, adapter fields, run examples, test command, spec links, and safety direction.

Tag:

nova-qbit-readme-v0.3

## Safety Direction

Allowed:

- safe text/UI/API adapter output
- contract-based external adapter execution
- owner approval flow
- safe project-root patching

Blocked:

- raw terminal execution through adapters
- automatic live call answering
- automatic outbound call without approval
- dangerous system mutation without approval
- hidden destructive actions

## Release Tags

- nova-qbit-whatsapp-adapter-v1
- nova-qbit-whatsapp-contract-v2
- nova-qbit-whatsapp-contract-v3
- nova-qbit-universal-adapter-v1
- nova-qbit-language-spec-v0.3
- nova-qbit-grammar-v0.3
- nova-qbit-adapter-contract-tests-v0.3
- nova-qbit-adapter-contract-ci-v0.3
- nova-qbit-readme-v0.3

## Release Status

NOVA/QBIT v0.3 is locked as a real experimental language contract milestone.

It is not a finished general-purpose programming language yet.

It is a working decision-language layer with parser/runtime examples, formal docs, tests, CI, and adapter contract proofs.
