# Universal Dragon Runtime Guardian

Mode: observe_only

Checks performed:

- Canonical systemd service state
- Canonical enablement
- Working directory contract
- ExecStart contract
- Restart thresholds
- Port PID ownership through service cgroups
- Local HTTP health
- PM2 name, status, cwd, script, PID and restarts
- Parked duplicate state
- Cloudflared process count and command contracts

Disabled actions:

- Automatic restart
- Automatic failover
- Service enable or disable
- Process termination
- Application patching
- Rollback execution

Safety contract:

[GUARD] owner_approval = REQUIRED
[GUARD] dangerous_action = DENY
