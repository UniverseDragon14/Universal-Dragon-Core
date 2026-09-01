# Universal Dragon Core Branch Map

Inspected on **2026-09-01**. All **23 reachable branches** are accounted for. The implementation tips were recorded before documentation-only audit commits.

| Branch | Inspected implementation tip | Purpose / state |
|---|---|---|
| `Uni` | `993a7caa7ef9` | NOVA install-page redirect |
| `agent/add-qbit-nova-language-artwork` | `9003a28ded8e` | QBIT NOVA hero artwork and install-page update |
| `agent/add-qbit-nova-language-link` | `27e848406bc3` | Development-repository link on install page |
| `agent/install-command-hub` | `823b769469a9` | Separate QBIT and NOVA command hub |
| `agent/openai-voice-reuse-cost-guard` | `a9be602c2f2e` | Voice gateway budget/reuse proof |
| `aslam/ecosystem-audit-and-roadmap` | `000e2f45865b` | Observe-only runtime guardian and roadmap |
| `aslam/eve-nova-core-clean-20260706_225525` | `16a24ba41c80` | EVE core cleanup removing Claude installer artifacts |
| `aslam/eve-nova-core-ready-20260706_220120` | `252000dc45a7` | EVE command/core scripts and example |
| `claude/fix-media-resolution-issue` | `630898c0cdd5` | Media-resolution API/UI performance fix |
| `claude/my-repo-url` | `7c7fa985d9e2` | Package metadata repository URL |
| `claude/novakutty-whatsapp-approval-eidit0` | `a09ebb47f7a4` | WhatsApp owner-approval control prototype |
| `coderabbitai/utg/918cd89` | `4cbd4b0bd3db` | Generated unit-test branch; also tracks node_modules artifacts |
| `codex/fix-media-resolution-perf-issue` | `8fe2aefa12ca` | Alternative media-resolution default fix |
| `copilot/fix-issue-in-file-processing` | `115cf8e1a887` | Chat file-processing route change |
| `copilot/fix-media-resolution-issue` | `a4e2031eb117` | Alternative media-resolution configuration fix |
| `feat/dragon-local-voice-v1` | `9ad91e309467` | Pi/local voice installer and second-SD validation |
| `feat/dragon-room-magic-voice-soul-v1` | `ebeee60b1b47` | Room voice/soul line with dependency-audit backlog |
| `main` | `e4914c5de2f2` | Older NOVA v1.3.3 runner/package line |
| `nova-v1.3.4-dev` | `ea8faac2d2c6` | NOVA v1.3.4 development package |
| `nova-v1.3.5-dev` | `b5684da7e6b8` | QBIT game plus dashboard integration |
| `nova-v1.4.0-dev` | `85cec2ae4dbe` | Current documented mixed QBIT history and web dashboard |
| `qbit-nova-game-v1` | `a6179a1f43bb` | QBIT NOVA game example checkpoint |
| `v0/universedragon14-f73a9cbd` | `99cb19b2f688` | Gemini model configuration snapshot |

## How to read this repository

These branches do not form one clean linear release train. They contain several lineages: NOVA packages, QBIT language/game history, the React control dashboard, EVE scripts, local voice, WhatsApp approval, install-site work, and isolated media/API fixes.

The default `nova-v1.4.0-dev` README documents the current mixed snapshot. A feature listed above is not automatically merged, deployed, hardware-connected, or production-safe.

## Review warnings

- `coderabbitai/utg/918cd89` tracks a large `node_modules` artifact set; do not merge it blindly.
- Media-resolution branches have overlapping alternatives and should be compared before choosing one.
- Voice, WhatsApp, MQTT, terminal and AI routes require authenticated deployment review.
- Dashboard telemetry includes demonstration values until wired to authenticated Pi/device sources.
- QBIT paths are software runtimes/simulators, not physical quantum hardware.
