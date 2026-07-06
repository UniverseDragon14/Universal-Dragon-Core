# Claude Code — run it in the Terminal AND in Termux

One installer that makes `claude` work in two places:

- **Terminal** (glibc Linux: Pi5, servers, WSL) — native `npm` install.
- **Termux** (Android phone) — a glibc userland via `proot-distro`, with a
  transparent `claude` launcher so it feels native on the phone.

## Why Termux needs the special path

On Termux, Node reports its platform as **`android`**, so npm never downloads
Claude Code's `linux-arm64` native binary and you hit:

```
Error: claude native binary not installed.
```

And even if you force that binary in, it's **glibc**-linked — it can't run on
Termux's **bionic** libc. The dependable fix on Android is to run Claude Code
inside a small glibc distro (Ubuntu) via `proot-distro`. This project automates
all of that and hides it behind a normal `claude` command.

## Quick start

```bash
# 1. get the project onto the device (git clone your repo, or copy this folder)
cd termux-claude-code

# 2. see what your device has and what to run
bash doctor.sh

# 3. install (auto-detects Termux vs terminal)
bash install.sh
```

Then, on **either** platform:

```bash
cd ~/my-project
claude
```

On Termux, that `claude` command drops you into the Ubuntu userland **in your
current directory** (files are bind-mounted 1:1 — edits land back in Termux
storage, nothing is copied), authenticates once, and runs exactly like the
desktop CLI.

## Manual paths (if you want to force one)

```bash
bash install.sh --glibc     # Pi5 / server / WSL
bash install.sh --termux    # Android/Termux
```

## What the installer does

| Path | Steps |
|------|-------|
| **glibc** | checks Node ≥ 18 → `npm i -g @anthropic-ai/claude-code` (with `--allow-scripts` so the postinstall fetches the native binary) → runs `install.cjs` as a fallback |
| **Termux** | `pkg install proot-distro` → `proot-distro install ubuntu` → inside Ubuntu: NodeSource Node 20 + `npm i -g @anthropic-ai/claude-code` → installs a Termux-side `claude` launcher |

Config knobs (env vars): `CLAUDE_DISTRO` (default `ubuntu`),
`CLAUDE_NODE_MAJOR` (default `20`).

## Auth notes

- First `claude` run prompts you to log in (browser link) or use an API key.
- The launcher passes `ANTHROPIC_API_KEY` / `CLAUDE_CODE_OAUTH_TOKEN` and any
  proxy vars through to the distro, and binds `$HOME` so `~/.claude` persists.

## Keep it alive in the background (Termux)

Same trick you used for the cloudflared tunnel:

```bash
nohup claude ... > ~/claude.log 2>&1 &
disown
```

For a long-running headless agent, prefer `tmux` (`pkg install tmux`) so you can
detach and reattach the session.

## Uninstall

```bash
# terminal
npm uninstall -g @anthropic-ai/claude-code
# termux
rm "$PREFIX/bin/claude"
proot-distro remove ubuntu     # optional: frees the rootfs
```
