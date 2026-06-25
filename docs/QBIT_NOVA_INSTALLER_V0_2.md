# QBIT NOVA Installer v0.2

Creator: Aslam
Project: Universal Dragon
Brain: NovaKutty
Team: Askutty
Language: QBIT NOVA

## Purpose

Install the QBIT NOVA CLI launcher as a simple command:

qnova

## Command After Install

qnova examples/v2/qbit_nova_cli_launcher_v02.qnova

## Truth Lock

QBIT NOVA is the language.
Host tools are bootstrap construction tools only.
Final target is self-hosting QBIT NOVA.

## Install Strategy

Termux:

Install to $PREFIX/bin/qnova when writable.

Fallback:

Install to ~/.local/bin/qnova.

## Safety

No delete-first action.
If qnova already exists, create a backup first.
No destructive action.
No fake quantum claim.

## Success Marker

QBIT_NOVA_INSTALLER_V02
