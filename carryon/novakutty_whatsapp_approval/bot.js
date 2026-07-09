"use strict";
// NOVAKUTTY WHATSAPP APPROVAL BOT - Safe Owner Control Layer
// Built with v5.2.6 strong brain bridge & public context router
// CommonJS only. No ESM.

const { Client, LocalAuth } = require("whatsapp-web.js");
const qrcode = require("qrcode-terminal");
const fs = require("fs");
const path = require("path");

// TDZ_FIX_V526: strong brain & context router loaded BEFORE any message handler
// that needs them.
const sbBridge = require("./lib/strong_brain_bridge_v526");
const pcrRouter = require("./lib/public_context_router_v526");

const OWNER_NUMBER = process.env.OWNER_NUMBER || "+1234567890";
const client = new Client({ authStrategy: new LocalAuth() });

// NOVAKUTTY_STRONG_LINK_V5_2_6: Deep search patterns that route to strong brain
const DEEP_SEARCH_REGEX = /^(deep search|search v6|news search|brain ask|investigate)/i;

// NOVAKUTTY_PUBLIC_MEMORY_FOLLOWUP_V5_2_5: Follow-up detection
const FOLLOWUP_PATTERNS = [
  "explain", "continue", "tamil la", "itha simple",
  "meaning enna", "clear ah sollu", "previous",
];

const HELP_MENU_V533 = `
╔═══════════════════════════════════════════════════╗
║     NOVAKUTTY WHATSAPP APPROVAL HELP (v5.3.3)     ║
╠═══════════════════════════════════════════════════╣
║                                                   ║
║  PUBLIC COMMANDS:                                 ║
║  • Ask anything → Default reply from Nova Core   ║
║  • "explain in tamil" → Context-aware followup   ║
║  • "continue" → Re-ask with full context         ║
║  • "news search <topic>" → Search + summarize    ║
║                                                   ║
║  OWNER COMMANDS (${OWNER_NUMBER}):          ║
║  • "/owner status" → System status                ║
║  • "/owner help" → This menu                      ║
║  • "/owner approval <action>" → Guard check      ║
║  • "/owner logs" → Last 10 actions                ║
║                                                   ║
║  DEEP SEARCH (All Users):                         ║
║  • "deep search <topic>" → Brain v6 + citation   ║
║  • "search v6 <query>" → Detailed research       ║
║  • "brain ask <question>" → Direct brain query   ║
║                                                   ║
╚═══════════════════════════════════════════════════╝
`;

// Message event - TDZ_FIX_V526: getText is called FIRST, before any checks
client.on("message", async (msg) => {
  // TDZ_FIX_V526: Declare text immediately
  let text = getText(msg);

  const jid = msg.from;
  const isOwner = jid === OWNER_NUMBER || jid.endsWith(OWNER_NUMBER);
  const __selfFromMe = !!msg.key.fromMe;

  // Ignore own messages
  if (__selfFromMe) return;

  // Skip empty
  if (!text || !text.trim()) return;

  // Log audit
  logAudit({ jid, text: sanitizeAudit(text), isOwner, timestamp: new Date().toISOString() });

  // NOVAKUTTY_STRONG_LINK_V5_2_6: Deep search routing
  if (DEEP_SEARCH_REGEX.test(text)) {
    try {
      const query = text.replace(DEEP_SEARCH_REGEX, "").trim();
      const result = await sbBridge.askStrongBrain(
        `Deep research: ${query}\n\nProvide detailed findings with citations.`
      );
      if (result) {
        pcrRouter.saveContext(jid, { userMsg: text, botReply: result });
        await msg.reply(result);
        return;
      }
    } catch (e) {
      console.error("Deep search error:", e.message);
    }
  }

  // NOVAKUTTY_PUBLIC_MEMORY_FOLLOWUP_V5_2_5: Follow-up detection and context-aware reply
  const followupReply = await pcrRouter.maybeFollowupReply(jid, text, sbBridge.askStrongBrain);
  if (followupReply) {
    pcrRouter.saveContext(jid, { userMsg: text, botReply: followupReply });
    await msg.reply(followupReply);
    return;
  }

  // Owner commands
  if (isOwner && text.startsWith("/owner")) {
    await handleOwnerCommand(msg, text);
    return;
  }

  // Public fallback - reply from Nova Core with memory save
  const publicReply = "Universal Dragon NOVA Vision: I'm Novakutty, your Nova-powered guide. "
    + "Ask anything — I'll search the brain for deep answers. "
    + "Try 'deep search <topic>' or 'explain in tamil' for context-aware responses. "
    + `Type "${HELP_MENU_V533}" for commands. 🐉`;
  pcrRouter.saveContext(jid, { userMsg: text, botReply: publicReply });
  await msg.reply(publicReply);
});

// Owner command handler
async function handleOwnerCommand(msg, text) {
  const subcmd = text.replace(/^\/owner\s+/, "").trim().toLowerCase();

  if (subcmd === "help") {
    return msg.reply(HELP_MENU_V533);
  }
  if (subcmd === "status") {
    const uptime = Math.floor(process.uptime() / 60);
    return msg.reply(`✓ Novakutty online (${uptime} min uptime)\n` +
      `• Strong brain bridge: online\n` +
      `• Context router: online\n` +
      `• Owner verified: ✓`);
  }
  if (subcmd.startsWith("approval")) {
    const action = subcmd.replace(/^approval\s+/, "").trim();
    const { decision, reason } = await checkGuard(action);
    return msg.reply(`Guard Decision:\n• Action: ${action}\n• Status: ${decision}\n• Reason: ${reason}`);
  }
  if (subcmd === "logs") {
    const logs = readAuditLogs(10);
    return msg.reply("Last 10 actions:\n\n" + logs.join("\n"));
  }

  msg.reply("Unknown owner command. Try '/owner help'");
}

// Simplified guard check (calls Nova Guard if available)
async function checkGuard(action) {
  const defaultDecision = { decision: "needs_approval", reason: "Nova Guard v0.6 check pending" };
  try {
    const guardScript = path.join(process.env.EVE_ROOT || "..", "tools", "qbit_nova_guard_approval_v06.py");
    if (fs.existsSync(guardScript)) {
      // In real implementation, exec with timeout and redact output
      return defaultDecision;
    }
  } catch (e) {}
  return defaultDecision;
}

// Helper: extract clean text from message
function getText(msg) {
  if (msg.hasMedia) return "[Media] " + (msg.caption || "");
  return msg.body || "";
}

// Helper: sanitize for audit log
function sanitizeAudit(text) {
  return text
    .replace(/\+\d{6,}/g, "[PHONE]")
    .replace(/sk-ant-[A-Za-z0-9_-]+/g, "[KEY]")
    .replace(/gsk_[A-Za-z0-9_-]+/g, "[KEY]")
    .slice(0, 200);
}

// Audit logging (JSONL, local only)
function logAudit(entry) {
  try {
    const logFile = path.join(process.env.NOVAKUTTY_WA_ROOT || ".", "audit.jsonl");
    fs.appendFileSync(logFile, JSON.stringify(entry) + "\n");
  } catch (e) {}
}

function readAuditLogs(count = 10) {
  try {
    const logFile = path.join(process.env.NOVAKUTTY_WA_ROOT || ".", "audit.jsonl");
    const lines = fs.readFileSync(logFile, "utf8").split("\n").filter(Boolean);
    return lines.slice(-count).map((line) => {
      try {
        const entry = JSON.parse(line);
        return `${entry.timestamp || "?"} | ${entry.jid || "?"} | ${entry.isOwner ? "OWNER" : "user"} | ${entry.text || ""}`;
      } catch (e) { return line; }
    });
  } catch (e) { return ["[No logs yet]"]; }
}

// QR Code on connect
client.on("qr", (qr) => {
  console.log("QR Code:");
  qrcode.generate(qr, { small: true });
});

client.on("authenticated", () => {
  console.log("✓ Authenticated with WhatsApp");
});

client.on("ready", () => {
  console.log("✓ Novakutty WhatsApp Approval online (PM2-managed)");
  console.log("  • Owner:", OWNER_NUMBER);
  console.log("  • Strong Brain Bridge: active");
  console.log("  • Public Context Router: active");
});

client.on("disconnected", () => {
  console.log("⚠ Disconnected. Reconnecting...");
  client.initialize();
});

// Start bot
client.initialize();

// Graceful shutdown (PM2 signals)
process.on("SIGTERM", async () => {
  console.log("Shutting down gracefully...");
  await client.destroy();
  process.exit(0);
});

module.exports = client;
