"use strict";
// NOVAKUTTY PUBLIC CONTEXT ROUTER V5.2.6  (CommonJS)
// Stronger public follow-up memory. Saves last turn context per chat JID and,
// when the next message is a follow-up ("explain in tamil", "continue",
// "itha simple ah sollu"...), answers using that context via the strong brain
// instead of a generic fallback. Secrets sanitized before writing. No shell.

const fs = require("fs");
const path = require("path");

const ROOT = process.env.NOVAKUTTY_WA_ROOT || process.cwd();
const MEM_DIR = path.join(ROOT, "memory", "followup");
try { fs.mkdirSync(MEM_DIR, { recursive: true }); } catch (e) {}

function sanitize(s) {
  return String(s || "")
    .replace(/sk-ant-[A-Za-z0-9_-]+/g, "[REDACTED_KEY]")
    .replace(/gsk_[A-Za-z0-9_-]+/g, "[REDACTED_KEY]")
    .replace(/AIza[A-Za-z0-9_-]+/g, "[REDACTED_KEY]")
    .replace(/OWNER_NUMBER\s*=\s*\S+/g, "OWNER_NUMBER=[REDACTED]")
    .replace(/\+\d{8,}/g, "[REDACTED_NUMBER]");
}

function safeJid(jid) {
  return String(jid || "unknown").replace(/[^a-zA-Z0-9_-]/g, "_").slice(0, 120);
}
function fileFor(jid) { return path.join(MEM_DIR, safeJid(jid) + ".json"); }

function saveContext(jid, ctx = {}) {
  try {
    const prev = loadContext(jid) || {};
    const next = {
      lastUserMsg: sanitize(ctx.userMsg != null ? ctx.userMsg : prev.lastUserMsg || ""),
      lastBotReply: sanitize(ctx.botReply != null ? ctx.botReply : prev.lastBotReply || ""),
      lastMediaType: ctx.mediaType != null ? ctx.mediaType : prev.lastMediaType || "",
      lastImageSummary: sanitize(ctx.imageSummary != null ? ctx.imageSummary : prev.lastImageSummary || ""),
      lastVoiceTranscript: sanitize(ctx.voiceTranscript != null ? ctx.voiceTranscript : prev.lastVoiceTranscript || ""),
      updatedAt: new Date().toISOString(),
    };
    fs.writeFileSync(fileFor(jid), JSON.stringify(next, null, 2));
    return next;
  } catch (e) { return null; }
}

function loadContext(jid) {
  try { return JSON.parse(fs.readFileSync(fileFor(jid), "utf8")); } catch (e) { return null; }
}

const FOLLOWUP_PATTERNS = [
  "explain", "explain this", "explain it", "explain in english", "explain in tamil",
  "explain tamil", "explain tamila", "tamil la explain", "tamila explain", "english la explain",
  "continue", "continue pannu", "itha explain", "itha simple", "simple ah sollu", "simplify",
  "previous answer", "previous meaning", "meaning enna", "adhula enna problem", "enna problem",
  "what happened", "that tire", "andha", "konjam clear", "clear ah sollu",
];

function isFollowup(text) {
  const t = String(text || "").toLowerCase().trim();
  if (!t) return false;
  if (t === "explain" || t === "continue" || t === "meaning") return true;
  return FOLLOWUP_PATTERNS.some((p) => t.includes(p));
}

// Fallback: read the bot's existing chat memory (memory/chats/<jid>.json,
// an array of {role,text}) so follow-ups work even before a v526 save.
function loadChatMemoryContext(jid) {
  try {
    const file = path.join(ROOT, "memory", "chats", safeJid(jid) + ".json");
    const arr = JSON.parse(fs.readFileSync(file, "utf8"));
    if (!Array.isArray(arr) || !arr.length) return null;
    let lastUser = "", lastBot = "";
    for (let i = arr.length - 1; i >= 0; i--) {
      const role = arr[i] && arr[i].role, txt = arr[i] && (arr[i].text || arr[i].content);
      if (!txt) continue;
      if (!lastBot && role === "assistant") lastBot = String(txt);
      else if (!lastUser && role === "user") lastUser = String(txt);
      if (lastUser && lastBot) break;
    }
    if (!lastUser && !lastBot) return null;
    return { lastUserMsg: sanitize(lastUser), lastBotReply: sanitize(lastBot),
      lastMediaType: "", lastImageSummary: "", lastVoiceTranscript: "" };
  } catch (e) { return null; }
}

function buildFollowupPrompt(jid, text) {
  const ctx = loadContext(jid) || loadChatMemoryContext(jid);
  if (!ctx) return null;
  const parts = [];
  if (ctx.lastUserMsg) parts.push("Previous user message: " + ctx.lastUserMsg);
  if (ctx.lastBotReply) parts.push("Previous assistant reply: " + ctx.lastBotReply);
  if (ctx.lastImageSummary) parts.push("Last image summary: " + ctx.lastImageSummary);
  if (ctx.lastVoiceTranscript) parts.push("Last voice transcript: " + ctx.lastVoiceTranscript);
  if (!parts.length) return null;
  parts.push("Now the user says: " + String(text || ""));
  parts.push("Answer the follow-up using the previous context. Reply in the language the user asked (Tamil/English). Be clear and specific, not generic.");
  return parts.join("\n");
}

// askFn: async (prompt) => string  (inject the strong brain bridge)
async function maybeFollowupReply(jid, text, askFn) {
  if (!isFollowup(text)) return "";
  const prompt = buildFollowupPrompt(jid, text);
  if (!prompt) {
    // Follow-up detected but no saved context -> one useful clarifying question.
    return "Edha explain pannanum bro? Andha last photo/voice/message-a sollunga, "
      + "illa konjam detail-a kelunga — naan andha context vachu sari-a sollுren. 🐉";
  }
  try {
    const ans = typeof askFn === "function" ? await askFn(prompt) : "";
    return (ans && ans.trim()) ? ans.trim() : "";
  } catch (e) { return ""; }
}

module.exports = {
  saveContext, loadContext, loadChatMemoryContext, isFollowup, buildFollowupPrompt, maybeFollowupReply, sanitize,
};
