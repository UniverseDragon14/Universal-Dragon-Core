# UD Terminal

Private iPhone web terminal for Universal Dragon / NOVA Pi5 access.

This is **not** a NOVA dashboard and not a remote-control button panel. It is a simple terminal-in-browser path:

```text
iPhone Safari / Chrome
    -> Tailscale tailnet HTTPS URL
    -> Raspberry Pi 5 localhost ttyd
    -> bash terminal
```

## Security rule

Do **not** expose this terminal publicly.

Use Tailscale Serve so only devices inside your tailnet can reach it. The terminal server listens on `127.0.0.1` only, and Tailscale proxies it safely to your private tailnet.

Never use Tailscale Funnel or public port forwarding for this terminal.

## Files

```text
ud-terminal/
├─ README.md
├─ scripts/
│  ├─ setup-pi-ttyd.sh
│  └─ start-tailnet-url.sh
└─ systemd/
   └─ ud-terminal.service
```

## Requirements

On Raspberry Pi 5:

- Raspberry Pi OS / Debian-based Linux
- `ttyd`
- Tailscale installed and logged in
- iPhone Tailscale app logged into the same tailnet

## Setup on Pi5

From this repository on the Pi5:

```bash
cd ~/ud-github-sync
bash ud-terminal/scripts/setup-pi-ttyd.sh
```

This installs `ttyd`, creates a user-level systemd service, and starts a local-only terminal server on:

```text
http://127.0.0.1:7681
```

## Start private iPhone access

```bash
bash ud-terminal/scripts/start-tailnet-url.sh
```

The script runs:

```bash
tailscale serve 7681
```

Tailscale prints a private HTTPS URL. Open that URL from iPhone Safari while the iPhone is connected to the same Tailscale account.

## Test locally on Pi5

```bash
curl -I http://127.0.0.1:7681
```

Expected: HTTP response from ttyd.

## Stop terminal service

```bash
systemctl --user stop ud-terminal.service
```

## Restart terminal service

```bash
systemctl --user restart ud-terminal.service
```

## Check logs

```bash
journalctl --user -u ud-terminal.service -n 80 --no-pager
```

## What this gives

- iPhone browser terminal
- Pi5 shell access
- No public exposure
- No NOVA dashboard
- No unsafe raw internet terminal

## Locked project idea

`UD Terminal` is a private iPhone web terminal for Pi5 using ttyd and Tailscale Serve.
