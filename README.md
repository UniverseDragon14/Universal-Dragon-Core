# Universal Dragon Core

This repository combines two active experimental tracks:

1. **QBIT NOVA language/runtime history** — Python-hosted parsers, QBC/QVM tools, examples, tests, installers, and design/proof documents.
2. **Universal Dragon web control dashboard** — React/Vite UI with an Express, Socket.IO, MQTT, and AI-chat server.

The current QBIT version marker is **1.4.0-dev**.

## Repository map

| Path | Current role |
|---|---|
| engine | earlier QBIT NOVA parser/token/runtime pipelines |
| tools | QN/QBC/QVM, guard, installer, packaging, and CLI utilities |
| tests | contract and regression scripts for the experimental language/runtime |
| examples/v2 | NOVA, QN, QNOVA, and UD examples |
| nova-lang | earlier NOVA language runtime, adapters, packages, and launchers |
| docs | specifications, milestones, proof notes, and truth-boundary documents |
| src | React control-room dashboard |
| server.ts | Express/Socket.IO server, AI chat route, MQTT bridge, and static app hosting |
| ud-terminal | local terminal service/setup helpers |

## Web dashboard

Requirements: Node.js and npm.

~~~bash
npm install
npm run dev
~~~

Useful checks:

~~~bash
npm run lint
npm run build
~~~

Optional server configuration is supplied through environment variables:

- PORT
- GROQ_API_KEY and optional GROQ_MODEL
- OPENAI_API_KEY and optional OPENAI_MODEL
- MQTT_BROKER and MQTT_TOPIC

Routes currently exposed by the server:

- GET /api/health
- POST /api/chat
- Socket.IO events for MQTT status and parsed Dragon Eye messages

## What is real and what is simulated

- AI chat can call Groq or OpenAI when a server-side key is configured.
- MQTT can subscribe to a configured broker and forward valid messages.
- The browser dashboard currently generates several CPU, temperature, spatial, log, and auto-code values with timers/random data. Those panels are demonstrations until they are connected to authenticated device telemetry.
- The QBIT code is a software language/runtime and virtual simulation research line. It does not turn a Raspberry Pi, phone, GPU, or CPU into physical quantum hardware.

## Security boundary

The server binds to all interfaces and the current chat route is not an authentication system. Keep development instances on a trusted network or place them behind authenticated TLS access, restrictive origins, rate limits, and request-size controls.

Never commit model keys, broker credentials, device addresses, approval tokens, private host data, or live audit exports.

## Project status

Research/development repository. The tests and receipts prove specific software paths only; they do not prove that every documented Pi service, robot, camera, WhatsApp bridge, or hardware module is live.
