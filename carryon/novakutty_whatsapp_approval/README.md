# Novakutty WhatsApp Approval — Safe Owner Control Layer

One WhatsApp bot. Two layers of protection. Linked to the strong brain.

```
             NOVAKUTTY WHATSAPP APPROVAL (v5.3.3)
        Built on QBIT NOVA + Carry-On core + Nova Guard
        
        PUBLIC    → Default reply, follow-up memory, deep search
        OWNER     → Guard approval, system status, action logs
```

## Install

```bash
cd Universal-Dragon-Core/carryon/novakutty_whatsapp_approval
npm install
export OWNER_NUMBER="+1234567890"  # Your WhatsApp number
npm run pm2-start
```

## Files

| File | Purpose |
|------|---------|
| `bot.js` | Main WhatsApp handler (CommonJS, PM2-managed) |
| `lib/strong_brain_bridge_v526.js` | Safe interface to strong brain (25s timeout, redacted secrets) |
| `lib/public_context_router_v526.js` | Follow-up memory + context detection (Tamil/English aware) |
| `package.json` | Dependencies + scripts |
| `memory/followup/` | Saved context per chat (JID-based) |
| `memory/chats/` | Original WhatsApp chat memory (fallback for context) |
| `audit.jsonl` | Action log (sanitized, no credentials) |

## Features

### Public Layer (All Users)

1. **Default Reply** — Ask anything, get Nova-powered response
2. **Follow-up Memory** — "Explain in tamil", "continue", "meaning enna?" → Uses last turn context
3. **Deep Search** — "deep search <topic>" → Routes to strong brain v6, returns citations
4. **Media Handling** — Images, voice → Summaries saved for follow-ups

### Owner Layer (OWNER_NUMBER Only)

1. **/owner help** — Full command menu
2. **/owner status** — System uptime, subsystem health
3. **/owner approval <action>** — Ask Nova Guard (allowed/needs_approval/blocked)
4. **/owner logs** — Last 10 chat actions (sanitized)

### Safety Constraints (Hardcoded)

- ✗ No hacking tools, stealth, hidden services
- ✗ No tracking people, phone numbers, photos, third-party accounts
- ✗ No credential access
- ✗ No live API calls unless explicitly approved
- ✗ No auto-push to GitHub
- ✗ No ESM (CommonJS only)
- ✓ Secrets redacted in logs + memory
- ✓ PM2 single-instance management
- ✓ Timeouts on all I/O (25s brain, audit append-only)

## Architecture

```
bot.js (Main Loop)
├─ getText(msg) → Extract text, handle media
├─ [TDZ_FIX_V526] Declare text BEFORE owner check
├─ [NOVAKUTTY_STRONG_LINK_V5_2_6] Deep search regex?
│  └─ askStrongBrain() → v526 bridge → ask_brain.js
├─ [NOVAKUTTY_PUBLIC_MEMORY_FOLLOWUP_V5_2_5] Follow-up detected?
│  └─ maybeFollowupReply() → load context → strong brain
├─ /owner commands? → handleOwnerCommand()
│  ├─ status → uptime + subsystems
│  ├─ approval → checkGuard()
│  └─ logs → readAuditLogs()
└─ Public fallback → Save context → Reply
```

## PM2 Management

```bash
# Start (watch mode, ignore memory/audit)
npm run pm2-start

# Restart (preserves memory)
npm run pm2-restart

# View logs (live)
npm run pm2-logs

# Stop
npm run pm2-stop

# Only PM2 can start/stop — never use nohup
# (dual instances cause WhatsApp Code 440 reconnect loop)
```

## Context Saving

Each chat (by JID) has a context file: `memory/followup/<jid_safe>.json`

```json
{
  "lastUserMsg": "what is quantum computing",
  "lastBotReply": "Quantum computing harnesses... [REDACTED_KEY]...",
  "lastMediaType": "image",
  "lastImageSummary": "A circuit diagram",
  "lastVoiceTranscript": "explain in tamil",
  "updatedAt": "2026-07-09T13:45:30Z"
}
```

Follow-ups like "explain in tamil" → build prompt → send to strong brain → get context-aware answer.

## Audit Logging

Append-only JSONL in `audit.jsonl` (sanitized):

```jsonl
{"jid":"123456789@c.us","text":"what is x?","isOwner":false,"timestamp":"2026-07-09T13:45:30Z"}
{"jid":"123456789@c.us","text":"[PHONE]","isOwner":false,"timestamp":"2026-07-09T13:46:00Z"}
```

No secrets, phone numbers, or API keys in logs. Safe to version-control (but still gitignore).

## Environment Variables

```bash
export OWNER_NUMBER="+1234567890"                    # Owner WhatsApp number
export NOVAKUTTY_WA_ROOT="/path/to/bot"              # Root for memory/ + audit.jsonl
export NOVAKUTTY_ASK_BRAIN="path/to/ask_brain.js"    # Strong brain entry point
export NOVAKUTTY_BRAIN_TIMEOUT_MS=25000              # Timeout (ms)
```

Default root: `process.cwd()` (current directory when bot starts).

## Testing

```bash
# Syntax check
npm test

# Manual start (single run)
node bot.js

# Via PM2 (production)
npm run pm2-start
```

Scan QR code in terminal. Start asking:

```
You: what is quantum computing
Bot: Universal Dragon NOVA Vision: ...

You: explain in tamil
Bot: [Context-aware Tamil explanation from strong brain]

You: deep search quantum supremacy
Bot: [Detailed research + citations]

OWNER_NUMBER: /owner help
Bot: [Help menu]
```

## Troubleshooting

### "WhatsApp Code 440" (Connection Replaced)

**Cause:** Two bot.js instances running (PM2 + manual nohup).

**Fix:**
```bash
# Kill ALL bot.js
pkill -f "novakutty-whatsapp-approval/bot.js"
# Use only PM2
npm run pm2-start
# Never use: nohup node bot.js
```

### Follow-up not working

**Check:**
1. `memory/followup/` directory exists and has JID files
2. `lastUserMsg` and `lastBotReply` are saved
3. Second message is detected as follow-up (27+ patterns in router)

**Debug:**
```bash
ls -la memory/followup/
cat memory/followup/123456789_c_us.json
npm run pm2-logs | grep "follow"
```

### Strong brain timeout

**Default:** 25s. Increase with:
```bash
export NOVAKUTTY_BRAIN_TIMEOUT_MS=35000
npm run pm2-restart
```

### Secrets in logs?

**Check:**
```bash
grep -i "sk-ant\|gsk_\|AIza\|OWNER" audit.jsonl memory/followup/*.json
```

Should return `[REDACTED]` or `[REDACTED_KEY]`. If not, redact manually.

## Version History

| Version | Change |
|---------|--------|
| v5.3.3 | Help menu + owner logs |
| v5.2.6 | Strong brain bridge + context router |
| v5.2.5 | Follow-up memory system |
| v5.1.0 | Initial owner approval |

## License

MIT. Built with ❤️ by Aslam & Nova Team.

---

**Questions?** Check `/owner help` in WhatsApp or read the code. The bot is boring on purpose — boring = safe.
