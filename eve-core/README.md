# EVE — Universal Dragon master command

**Forged by Aslam.** One command to awaken the whole world, running the same in
**Termux** (Android) and the **terminal** (Pi5 / glibc). Built on Aslam's
**QBIT NOVA** language (quantum-level, `SAFE_BOOTSTRAP`) and the Carry-On core,
with everything routed through **Nova Guard** — safe by default, no destructive
OS actions.

```
./eve mythos
```

```
        ______     _______
       / ____/  ___/ / ____/
      / __/  \/ _ \ / __/       U N I V E R S A L   D R A G O N
     / /___ /  __/  /___
    /_____/  \___/_____/         E · V · E   ·   N O V A   C O R E
```

## Install (Termux or Pi5)

```bash
cd Universal-Dragon-Core
chmod +x eve                 # once, if needed
./eve doctor                 # check every subsystem is ready
./eve install-cli            # optional: type `eve` from anywhere (also `nova`)
```

No extra dependencies for the core — pure `bash` + your existing `python3`.
`node`/`ffmpeg` are only needed for the WhatsApp + media subsystems.

## Commands

| Command | What it does |
|---------|--------------|
| `./eve mythos` | Awaken & map the whole world (safe — launches nothing) |
| `./eve mythos --boot` | Awaken **and** start the live daemons |
| `./eve doctor` | Readiness of every subsystem |
| `./eve status` / `./eve down` | Show / stop running daemons |
| `./eve run <file>` | Run a QBIT NOVA program (`.qn` / `.qnova` / `.ud`) |
| `./eve qbc <file>` | Compile-inspect a program (token/ast/ir/qbc counts) |
| `./eve guard <action>` | Ask Nova Guard: allowed / needs_approval / blocked |
| `./eve gateway [start\|stop]` | Carry-On authenticated command gateway |
| `./eve whatsapp [start\|stop]` | WhatsApp voice engine (+ Node bridge) |
| `./eve media <args…>` | Media pipeline (`./eve media probe in.mp4`) |
| `./eve install-cli` | Put `eve` on your PATH |
| `./eve version` | Version |

`nova` is a symlink to `eve` — both names work.

## Try it

```bash
./eve run examples/eve/awaken.qn      # a real QBIT NOVA program, runs GREEN
./eve guard delete                    # -> blocked by Nova Guard
./eve guard network                   # -> needs_approval
```

## Boot the live world

```bash
export CARRYON_GATEWAY_SECRET="$(head -c 32 /dev/urandom | base64)"   # for the gateway
./eve mythos --boot
./eve status
./eve down            # stop everything
```

Daemon PIDs/logs live under `.eve/run/` (gitignored). On Termux, keep the world
alive across app-close the same way you kept `cloudflared` up:

```bash
nohup ./eve mythos --boot > ~/eve.log 2>&1 &
disown
```

## Architecture

```
eve                     # dispatcher (bash) — the ./eve command
eve-core/
  env.sh                # platform detect (termux/glibc), python resolver, logging
  banner.sh             # Universal Dragon / EVE mythos art
  mythos.sh             # `eve mythos` — the grand awakening
  run.sh                # QBIT NOVA language runner (-> tools/qnova)
  guard.sh              # Nova Guard bridge (-> tools/qbit_nova_guard_approval)
  stack.sh              # daemon lifecycle (-> carryon/*)
  doctor.sh             # readiness checks
examples/eve/awaken.qn  # runnable demo program
```

EVE is a thin, robust orchestration skin over your existing engines — it doesn't
reimplement them, it awakens them.
