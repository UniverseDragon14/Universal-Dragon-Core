import express from "express";
import { createServer as createViteServer } from "vite";
import { Server } from "socket.io";
import http from "http";
import mqtt from "mqtt";
import path from "path";
import { timingSafeEqual } from "crypto";
import { fileURLToPath } from "url";
import { mkdir, readFile, rename, writeFile } from "fs/promises";
import { planVoiceSoul, type DragonContext, type DragonMood } from "./src/voice/voiceSoul";
import { renderElevenV3Prompt } from "./src/voice/elevenV3";
import {
  buildOpenAITtsInstructions,
  getDragonVoiceProfile,
  listDragonVoiceProfiles,
} from "./src/voice/openaiTts";
import {
  parsePositiveInteger,
  reserveVoiceBudget,
  resolveDragonVoiceProvider,
  utcVoiceUsageDate,
  type DragonVoiceProvider,
  type VoiceBudgetLimits,
} from "./src/voice/voiceBudget";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

type ChatMessage = {
  role: "user" | "assistant" | "system";
  content: string;
};

const NOVA_SYSTEM = `You are NOVA, the Universal Dragon assistant created by Aslam.
Speak in simple Tamil + Tanglish when useful.
Be practical, safe, concise, and approval-first.
Never ask for or expose API keys, tokens, private data, or passwords.
For risky actions, give a plan and ask for explicit yes/no approval.`;

const DRAGON_MOODS = new Set<DragonMood>(["CALM", "PLAYFUL", "CURIOUS", "SERIOUS", "WHISPER"]);
const DRAGON_CONTEXTS = new Set<DragonContext>(["WAKE", "CHAT", "ALERT"]);
let voiceRequestInFlight = false;

function activeVoiceProvider(): DragonVoiceProvider {
  return resolveDragonVoiceProvider(process.env.DRAGON_VOICE_PROVIDER);
}

function voiceProviderModel(provider: DragonVoiceProvider): string {
  if (provider === "openai") return process.env.OPENAI_TTS_MODEL || "gpt-4o-mini-tts";
  if (provider === "elevenlabs") return process.env.ELEVENLABS_MODEL || "eleven_v3";
  return "local-client-tts";
}

function isVoiceProviderConfigured(provider: DragonVoiceProvider): boolean {
  if (provider === "local") return true;
  if (provider === "openai") return Boolean(process.env.OPENAI_API_KEY);
  return Boolean(process.env.ELEVENLABS_API_KEY && process.env.ELEVENLABS_VOICE_ID);
}

function voiceBudgetLimits(): VoiceBudgetLimits {
  return {
    maxRequests: parsePositiveInteger(process.env.DRAGON_VOICE_DAILY_MAX_REQUESTS, 6),
    maxCharacters: parsePositiveInteger(process.env.DRAGON_VOICE_DAILY_MAX_CHARACTERS, 2400),
  };
}

function voiceMaxInputChars(): number {
  return parsePositiveInteger(process.env.DRAGON_VOICE_MAX_INPUT_CHARS, 400);
}

function voiceUsageFile(): string {
  return process.env.DRAGON_VOICE_USAGE_FILE
    || path.join(process.cwd(), "data", "dragon-voice-usage.json");
}

async function reservePaidVoiceBudget(inputCharacters: number) {
  const usageFile = voiceUsageFile();
  const usageDate = utcVoiceUsageDate(new Date());
  let current: unknown;

  try {
    const raw = await readFile(usageFile, "utf8");
    current = JSON.parse(raw);
  } catch (error: any) {
    if (error?.code !== "ENOENT") {
      throw new Error("voice_budget_state_unavailable");
    }
  }

  if (current !== undefined && (
    !current
    || typeof current !== "object"
    || Array.isArray(current)
  )) {
    throw new Error("voice_budget_state_unavailable");
  }

  const reservation = reserveVoiceBudget(current, voiceBudgetLimits(), inputCharacters, usageDate);
  if (!reservation.allowed) return reservation;

  try {
    await mkdir(path.dirname(usageFile), { recursive: true });
    const tempFile = usageFile + "." + process.pid + ".tmp";
    await writeFile(tempFile, JSON.stringify(reservation.next) + "\n", {
      encoding: "utf8",
      mode: 0o600,
    });
    await rename(tempFile, usageFile);
  } catch {
    throw new Error("voice_budget_state_unavailable");
  }

  return reservation;
}

function safeTokenMatch(candidate: string, expected: string): boolean {
  if (!candidate || !expected) return false;

  const candidateBytes = Buffer.from(candidate, "utf8");
  const expectedBytes = Buffer.from(expected, "utf8");

  if (candidateBytes.length !== expectedBytes.length) return false;
  return timingSafeEqual(candidateBytes, expectedBytes);
}

function authorizeVoiceRequest(req: express.Request): "ok" | "disabled" | "unauthorized" {
  const expected = process.env.DRAGON_VOICE_ACCESS_TOKEN || "";
  if (!expected) return "disabled";

  const authorization = req.header("authorization") || "";
  const match = authorization.match(/^Bearer\s+(.+)$/i);
  const candidate = match?.[1]?.trim() || "";

  return safeTokenMatch(candidate, expected) ? "ok" : "unauthorized";
}

async function callOpenAICompatible(messages: ChatMessage[]) {
  const groqKey = process.env.GROQ_API_KEY || "";
  const openaiKey = process.env.OPENAI_API_KEY || "";

  const isGroq = Boolean(groqKey);
  const apiKey = groqKey || openaiKey;

  if (!apiKey) {
    return {
      ok: false,
      provider: "none",
      model: "none",
      text: "NOVA brain key missing on server. Set GROQ_API_KEY first."
    };
  }

  const endpoint = isGroq
    ? "https://api.groq.com/openai/v1/chat/completions"
    : "https://api.openai.com/v1/chat/completions";

  const model = isGroq
    ? (process.env.GROQ_MODEL || "openai/gpt-oss-120b")
    : (process.env.OPENAI_MODEL || "gpt-4.1-mini");

  const response = await fetch(endpoint, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${apiKey}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      model,
      messages: [
        { role: "system", content: NOVA_SYSTEM },
        ...messages.slice(-12)
      ],
      temperature: 0.6,
      max_tokens: 450
    })
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`AI provider error ${response.status}: ${errorText.slice(0, 260)}`);
  }

  const data = await response.json();
  const text = data?.choices?.[0]?.message?.content || "NOVA brain returned empty response.";

  return {
    ok: true,
    provider: isGroq ? "groq" : "openai",
    model,
    text
  };
}

async function generateElevenV3Speech(plan: ReturnType<typeof planVoiceSoul>) {
  const apiKey = process.env.ELEVENLABS_API_KEY || "";
  const voiceId = process.env.ELEVENLABS_VOICE_ID || "";
  const model = process.env.ELEVENLABS_MODEL || "eleven_v3";

  if (!apiKey || !voiceId) {
    return {
      ok: false as const,
      reason: "voice_provider_not_configured",
      model,
    };
  }

  const providerText = renderElevenV3Prompt(plan);
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 45_000);

  try {
    const endpoint = new URL(
      "https://api.elevenlabs.io/v1/text-to-speech/" + encodeURIComponent(voiceId),
    );
    endpoint.searchParams.set("output_format", "mp3_44100_128");

    const response = await fetch(endpoint, {
      method: "POST",
      headers: {
        "xi-api-key": apiKey,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
      },
      body: JSON.stringify({
        text: providerText,
        model_id: model,
      }),
      signal: controller.signal,
    });

    if (!response.ok) {
      throw new Error("ElevenLabs voice request failed with status " + response.status);
    }

    return {
      ok: true as const,
      model,
      plan,
      audio: Buffer.from(await response.arrayBuffer()),
      requestId: response.headers.get("request-id") || "",
      characterCost: response.headers.get("character-cost") || "",
    };
  } finally {
    clearTimeout(timeout);
  }
}

async function generateOpenAITtsSpeech(
  plan: ReturnType<typeof planVoiceSoul>,
  profile: ReturnType<typeof getDragonVoiceProfile>,
) {
  const apiKey = process.env.OPENAI_API_KEY || "";
  const model = process.env.OPENAI_TTS_MODEL || "gpt-4o-mini-tts";

  if (!apiKey) {
    return {
      ok: false as const,
      reason: "voice_provider_not_configured",
      model,
    };
  }

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 45_000);

  try {
    const response = await fetch("https://api.openai.com/v1/audio/speech", {
      method: "POST",
      headers: {
        "Authorization": "Bearer " + apiKey,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
      },
      body: JSON.stringify({
        model,
        voice: profile.openaiVoice,
        input: plan.spokenText,
        instructions: buildOpenAITtsInstructions(plan, profile),
        response_format: "mp3",
      }),
      signal: controller.signal,
    });

    if (!response.ok) {
      throw new Error("OpenAI voice request failed with status " + response.status);
    }

    return {
      ok: true as const,
      model,
      plan,
      profile,
      audio: Buffer.from(await response.arrayBuffer()),
      requestId: response.headers.get("x-request-id") || "",
      characterCost: "",
    };
  } finally {
    clearTimeout(timeout);
  }
}

async function startServer() {
  const app = express();
  const server = http.createServer(app);
  const io = new Server(server);
  const PORT = Number(process.env.PORT || 3000);

  app.use(express.json({ limit: "1mb" }));

  const MQTT_BROKER = process.env.MQTT_BROKER || "mqtt://192.168.70.196";
  const MQTT_TOPIC = process.env.MQTT_TOPIC || "UniversalDragon/NOVA/Reply";

  const mqttClient = mqtt.connect(MQTT_BROKER, {
    connectTimeout: 15000,
    reconnectPeriod: 30000,
    manualConnect: false,
  });

  mqttClient.on("connect", () => {
    console.log("✅ MQTT Connected to " + MQTT_BROKER);
    mqttClient.subscribe(MQTT_TOPIC);
    io.emit("mqtt_status", { connected: true, broker: MQTT_BROKER });
  });

  mqttClient.on("message", (topic, message) => {
    const msgStr = message.toString();
    if (msgStr.startsWith("[DETECT]")) {
      try {
        const jsonStr = msgStr.replace("[DETECT] ", "");
        const detection = JSON.parse(jsonStr);
        io.emit("dragon_eye_detection", detection);
      } catch (e) {
        console.error("Failed to parse MQTT detection:", e);
      }
    }
  });

  mqttClient.on("error", (err) => {
    if (err.message.includes("connack timeout")) {
      console.warn(`📡 MQTT Timeout: Broker at ${MQTT_BROKER} is unreachable from this cloud environment. This is expected for local network IPs.`);
    } else {
      console.warn("⚠️ MQTT Connection Error:", err.message);
    }
    io.emit("mqtt_status", { connected: false, error: err.message, broker: MQTT_BROKER });
  });

  mqttClient.on("offline", () => {
    io.emit("mqtt_status", { connected: false, status: "offline" });
  });

  app.get("/api/health", (req, res) => {
    const provider = activeVoiceProvider();
    res.json({
      status: "ok",
      mqtt: mqttClient.connected,
      ai_provider: process.env.GROQ_API_KEY ? "groq" : process.env.OPENAI_API_KEY ? "openai" : "missing",
      model: process.env.GROQ_API_KEY ? (process.env.GROQ_MODEL || "openai/gpt-oss-120b") : (process.env.OPENAI_MODEL || "gpt-4.1-mini"),
      voice: {
        provider,
        configured: Boolean(process.env.DRAGON_VOICE_ACCESS_TOKEN) && isVoiceProviderConfigured(provider),
        protected: true,
        model: voiceProviderModel(provider),
        paid_provider: provider !== "local",
        daily_limits: provider === "local" ? null : voiceBudgetLimits(),
      },
    });
  });

  app.get("/api/voice/status", (req, res) => {
    const provider = activeVoiceProvider();
    res.json({
      ok: true,
      provider,
      configured: Boolean(process.env.DRAGON_VOICE_ACCESS_TOKEN) && isVoiceProviderConfigured(provider),
      protected: true,
      model: voiceProviderModel(provider),
      paid_provider: provider !== "local",
      explicit_premium_opt_in_required: provider !== "local",
      profiles: listDragonVoiceProfiles(),
      default_profile: getDragonVoiceProfile(process.env.DRAGON_VOICE_DEFAULT_PROFILE).id,
      max_input_chars: voiceMaxInputChars(),
      daily_limits: provider === "local" ? null : voiceBudgetLimits(),
      voice_id_exposed: false,
    });
  });

  app.post("/api/voice/speak", async (req, res) => {
    const auth = authorizeVoiceRequest(req);

    if (auth === "disabled") {
      return res.status(503).json({ ok: false, error: "voice_api_disabled" });
    }

    if (auth === "unauthorized") {
      res.setHeader("WWW-Authenticate", "Bearer");
      return res.status(401).json({ ok: false, error: "unauthorized" });
    }

    if (voiceRequestInFlight) {
      return res.status(429).json({ ok: false, error: "voice_busy" });
    }

    voiceRequestInFlight = true;

    try {
      const rawText = String(req.body?.text || "").trim();
      const maxInputChars = voiceMaxInputChars();
      const requestedMood = String(req.body?.mood || "PLAYFUL").toUpperCase() as DragonMood;
      const requestedContext = String(req.body?.context || "CHAT").toUpperCase() as DragonContext;

      if (!rawText) {
        return res.status(400).json({ ok: false, error: "text_required" });
      }

      if (rawText.length > maxInputChars) {
        return res.status(400).json({
          ok: false,
          error: "voice_input_too_long",
          max_input_chars: maxInputChars,
        });
      }

      const mood: DragonMood = DRAGON_MOODS.has(requestedMood) ? requestedMood : "CALM";
      const context: DragonContext = DRAGON_CONTEXTS.has(requestedContext) ? requestedContext : "CHAT";
      const plan = planVoiceSoul({ text: rawText, mood, context });

      if (!plan.spokenText) {
        return res.status(400).json({ ok: false, error: "voice_text_empty_after_sanitize" });
      }

      const requestedProfile = req.body?.voice_profile || req.body?.voiceProfile;
      const profile = getDragonVoiceProfile(
        typeof requestedProfile === "string"
          ? requestedProfile
          : process.env.DRAGON_VOICE_DEFAULT_PROFILE,
      );
      const provider = activeVoiceProvider();

      if (provider === "local") {
        return res.status(202).json({
          ok: true,
          action: "client_tts",
          ai_generated: false,
          provider: "local",
          text: plan.spokenText,
          mood: plan.mood,
          profile: profile.id,
        });
      }

      if (req.body?.premium !== true) {
        return res.status(409).json({
          ok: false,
          error: "premium_voice_opt_in_required",
          provider,
        });
      }

      if (!isVoiceProviderConfigured(provider)) {
        return res.status(503).json({
          ok: false,
          error: "voice_provider_not_configured",
          provider,
          model: voiceProviderModel(provider),
        });
      }

      const budget = await reservePaidVoiceBudget(plan.spokenText.length);
      if (!budget.allowed) {
        return res.status(429).json({
          ok: false,
          error: budget.reason,
          provider,
          daily_usage: budget.next,
          daily_limits: voiceBudgetLimits(),
        });
      }

      const result = provider === "openai"
        ? await generateOpenAITtsSpeech(plan, profile)
        : await generateElevenV3Speech(plan);

      if (!result.ok) {
        return res.status(503).json({
          ok: false,
          error: result.reason,
          provider,
          model: result.model,
        });
      }

      res.setHeader("Content-Type", "audio/mpeg");
      res.setHeader("Cache-Control", "no-store");
      res.setHeader("X-Dragon-AI-Generated", "true");
      res.setHeader("X-Dragon-Voice-Provider", provider);
      res.setHeader("X-Dragon-Voice-Profile", profile.id);
      res.setHeader("X-Dragon-Voice-Mood", result.plan.mood);
      res.setHeader("X-Dragon-Voice-Model", result.model);
      if (result.requestId) res.setHeader("X-Provider-Request-Id", result.requestId);
      if (result.characterCost) res.setHeader("X-Provider-Character-Cost", result.characterCost);
      return res.send(result.audio);
    } catch (error: any) {
      const message = error?.name === "AbortError"
        ? "voice_provider_timeout"
        : error?.message === "voice_budget_state_unavailable"
          ? "voice_budget_state_unavailable"
          : "voice_generation_failed";
      console.error("Dragon voice error:", message);
      return res.status(502).json({ ok: false, error: message });
    } finally {
      voiceRequestInFlight = false;
    }
  });

  app.post("/api/chat", async (req, res) => {
    try {
      const input = String(req.body?.message || "").trim();
      const history = Array.isArray(req.body?.history) ? req.body.history : [];

      if (!input) {
        return res.status(400).json({ ok: false, error: "message_required" });
      }

      const safeHistory: ChatMessage[] = history
        .filter((m: any) => (m?.role === "user" || m?.role === "assistant") && typeof m?.content === "string")
        .slice(-10)
        .map((m: any) => ({ role: m.role, content: m.content.slice(0, 3000) }));

      const result = await callOpenAICompatible([
        ...safeHistory,
        { role: "user", content: input.slice(0, 3000) }
      ]);

      res.json(result);
    } catch (error: any) {
      console.error("NOVA chat error:", error?.message || error);
      res.status(500).json({
        ok: false,
        error: "nova_chat_failed",
        text: "NOVA brain connection failed. Check GROQ_API_KEY / model on server."
      });
    }
  });

  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  server.listen(PORT, "0.0.0.0", () => {
    console.log(`🚀 Universal Dragon Server running on http://localhost:${PORT}`);
    console.log(`📡 MQTT Broker: ${MQTT_BROKER}`);
    console.log(`🧠 NOVA AI Provider: ${process.env.GROQ_API_KEY ? "Groq" : process.env.OPENAI_API_KEY ? "OpenAI" : "Missing key"}`);
    const provider = activeVoiceProvider();
    console.log(
      "🎙️ Dragon Voice: " + provider + (
        isVoiceProviderConfigured(provider) && process.env.DRAGON_VOICE_ACCESS_TOKEN
          ? " protected endpoint ready"
          : " not configured"
      ),
    );
    console.log(`🔗 Socket.io: Active`);
  });
}

startServer();
