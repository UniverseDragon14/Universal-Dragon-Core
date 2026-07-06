#!/usr/bin/env node
/**
 * WhatsApp <-> Carry-On spool bridge (Baileys).
 *
 * Responsibilities:
 *   1. Own the WhatsApp Web multi-device socket (auth persisted to ./auth).
 *   2. On an incoming voice note (PTT), download the audio and drop a job JSON
 *      into spool/whatsapp/inbox for the Python engine.
 *   3. Watch spool/whatsapp/outbox and send back the synthesized reply.
 *
 * MCP-safe logging: this bridge is designed to run under an MCP stdio host, so
 * every log line goes to process.stderr and stdout is never written to. If you
 * later expose this as an MCP server, stdout stays a clean JSON-RPC channel.
 *
 * Scope note: Baileys delivers voice *messages*, not live call media. WhatsApp
 * call audio is E2E-encrypted WebRTC and is not available to a userland client.
 *
 * Install:  npm install   (see package.json in this folder)
 * Run:      node index.js
 */
import { existsSync, mkdirSync, readdirSync, renameSync, rmSync, writeFileSync } from 'node:fs';
import { readFile } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { randomUUID } from 'node:crypto';

import makeWASocket, {
  DisconnectReason,
  downloadMediaMessage,
  useMultiFileAuthState,
} from '@whiskeysockets/baileys';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SPOOL = process.env.CARRYON_SPOOL || resolve(__dirname, '..', '..', 'spool', 'whatsapp');
const INBOX = join(SPOOL, 'inbox');
const OUTBOX = join(SPOOL, 'outbox');
const MEDIA = join(SPOOL, 'media');
const AUTH_DIR = process.env.CARRYON_WA_AUTH || join(__dirname, 'auth');

// Optional allowlist: only react to these chat ids (comma-separated). Empty = all.
const ALLOW = (process.env.CARRYON_WA_ALLOW || '')
  .split(',').map((s) => s.trim()).filter(Boolean);

const log = (...a) => console.error('[wa.bridge]', ...a); // stderr only

for (const d of [INBOX, OUTBOX, MEDIA, AUTH_DIR]) {
  if (!existsSync(d)) mkdirSync(d, { recursive: true });
}

function isVoiceNote(msg) {
  const a = msg.message?.audioMessage;
  return Boolean(a && a.ptt);
}

async function handleVoice(sock, msg) {
  const chatId = msg.key.remoteJid;
  if (ALLOW.length && !ALLOW.includes(chatId)) return;

  const id = randomUUID().replace(/-/g, '');
  const audioPath = join(MEDIA, `${id}.ogg`);
  const buffer = await downloadMediaMessage(msg, 'buffer', {}, { logger: undefined, reuploadRequest: sock.updateMediaMessage });
  writeFileSync(audioPath, buffer);

  const job = {
    id,
    chat_id: chatId,
    message_id: msg.key.id,
    audio_path: audioPath,
    ts: Date.now() / 1000,
  };
  const tmp = join(INBOX, `${id}.job.json.tmp`);
  const final = join(INBOX, `${id}.job.json`);
  writeFileSync(tmp, JSON.stringify(job));
  renameSync(tmp, final); // atomic; engine only ever sees a complete job
  log('inbound voice queued', id, chatId);
}

function watchOutbox(sock) {
  setInterval(async () => {
    let names;
    try {
      names = readdirSync(OUTBOX).filter((n) => n.endsWith('.job.json'));
    } catch {
      return;
    }
    for (const name of names.sort()) {
      const jobPath = join(OUTBOX, name);
      try {
        const job = JSON.parse(await readFile(jobPath, 'utf8'));
        const audio = await readFile(job.reply_audio);
        await sock.sendMessage(job.chat_id, {
          audio,
          ptt: true,
          mimetype: 'audio/ogg; codecs=opus',
        });
        log('reply sent', job.id, job.chat_id);
        rmSync(jobPath, { force: true });
        rmSync(job.reply_audio, { force: true });
      } catch (err) {
        log('outbox send failed', name, String(err));
      }
    }
  }, Number(process.env.CARRYON_OUTBOX_POLL_MS || 1000));
}

async function start() {
  const { state, saveCreds } = await useMultiFileAuthState(AUTH_DIR);
  const sock = makeWASocket({ auth: state, printQRInTerminal: true });

  sock.ev.on('creds.update', saveCreds);

  sock.ev.on('connection.update', ({ connection, lastDisconnect }) => {
    if (connection === 'close') {
      const code = lastDisconnect?.error?.output?.statusCode;
      const retry = code !== DisconnectReason.loggedOut;
      log('connection closed', code, 'retry:', retry);
      if (retry) start();
    } else if (connection === 'open') {
      log('WhatsApp connected');
    }
  });

  sock.ev.on('messages.upsert', async ({ messages }) => {
    for (const msg of messages) {
      if (!msg.message || msg.key.fromMe) continue;
      if (isVoiceNote(msg)) {
        try {
          await handleVoice(sock, msg);
        } catch (err) {
          log('inbound handling failed', String(err));
        }
      }
    }
  });

  watchOutbox(sock);
}

start().catch((err) => {
  log('fatal', String(err));
  process.exit(1);
});
