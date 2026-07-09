"use strict";
// NOVAKUTTY STRONG BRAIN BRIDGE V5.2.6  (CommonJS)
// Calls the strong brain CLI safely via execFile (NO shell string), with a
// timeout, redacts secrets from output, and returns clean text. Fail-safe:
// on any error/timeout it returns "" so the caller keeps its existing flow.

const { execFile } = require("child_process");
const path = require("path");

const ASK_BRAIN = process.env.NOVAKUTTY_ASK_BRAIN
  || path.join(process.env.HOME || "", "novakutty-dragon-brain", "tools", "ask_brain.js");
const TIMEOUT_MS = Number(process.env.NOVAKUTTY_BRAIN_TIMEOUT_MS || 25000);

function redact(s) {
  return String(s || "")
    .replace(/sk-ant-[A-Za-z0-9_-]+/g, "[REDACTED_KEY]")
    .replace(/gsk_[A-Za-z0-9_-]+/g, "[REDACTED_KEY]")
    .replace(/AIza[A-Za-z0-9_-]+/g, "[REDACTED_KEY]")
    .replace(/ya29\.[A-Za-z0-9_-]+/g, "[REDACTED_KEY]")
    .replace(/ghp_[A-Za-z0-9_]+/g, "[REDACTED_KEY]")
    .replace(/(OPENAI|GROQ|GEMINI|KIMI|QWEN|SHORTIO|ANTHROPIC)_API_KEY\s*=\s*\S+/gi, "$1_API_KEY=[REDACTED]")
    .replace(/OWNER_NUMBER\s*=\s*\S+/g, "OWNER_NUMBER=[REDACTED]")
    .replace(/\+\d{8,}/g, "[REDACTED_NUMBER]");
}

function askStrongBrain(question) {
  return new Promise((resolve) => {
    const q = String(question || "").trim();
    if (!q) { resolve(""); return; }
    try {
      execFile("node", [ASK_BRAIN, q],
        { timeout: TIMEOUT_MS, maxBuffer: 4 * 1024 * 1024 },
        (err, stdout) => {
          if (err && !stdout) { resolve(""); return; }
          resolve(redact(String(stdout || "")).trim());
        });
    } catch (e) { resolve(""); }
  });
}

module.exports = { askStrongBrain, redact, ASK_BRAIN };
