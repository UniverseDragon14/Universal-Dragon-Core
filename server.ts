import express from "express";
import { createServer as createViteServer } from "vite";
import { Server } from "socket.io";
import http from "http";
import mqtt from "mqtt";
import path from "path";
import { fileURLToPath } from "url";
import { planVoiceSoul, type DragonContext, type DragonMood } from "./src/voice/voiceSoul";
import { renderElevenV3Prompt } from "./src/voice/elevenV3";

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

async function generateElevenV3Speech(text: string, mood: DragonMood, context: DragonContext) {
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

  const plan = planVoiceSoul({ text, mood, context });
  const providerText = renderElevenV3Prompt(plan);
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 45_000);

  try {
    const endpoint = new URL(
      `https://api.elevenlabs.io/v1/text-to-speech/${encodeURIComponent(voiceId)}`,
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
      const detail = (await response.text()).slice(0, 320);
      throw new Error(`ElevenLabs error ${response.status}: ${detail}`);
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
    res.json({
      status: "ok",
      mqtt: mqttClient.connected,
      ai_provider: process.env.GROQ_API_KEY ? "groq" : process.env.OPENAI_API_KEY ? "openai" : "missing",
      model: process.env.GROQ_API_KEY ? (process.env.GROQ_MODEL || "openai/gpt-oss-120b") : (process.env.OPENAI_MODEL || "gpt-4.1-mini"),
      voice: {
        provider: "elevenlabs",
        configured: Boolean(process.env.ELEVENLABS_API_KEY && process.env.ELEVENLABS_VOICE_ID),
        model: process.env.ELEVENLABS_MODEL || "eleven_v3",
      },
    });
  });

  app.get("/api/voice/status", (req, res) => {
    res.json({
      ok: true,
      provider: "elevenlabs",
      configured: Boolean(process.env.ELEVENLABS_API_KEY && process.env.ELEVENLABS_VOICE_ID),
      model: process.env.ELEVENLABS_MODEL || "eleven_v3",
      voice_id_exposed: false,
    });
  });

  app.post("/api/voice/speak", async (req, res) => {
    try {
      const text = String(req.body?.text || "").trim().slice(0, 1200);
      const requestedMood = String(req.body?.mood || "PLAYFUL").toUpperCase() as DragonMood;
      const requestedContext = String(req.body?.context || "CHAT").toUpperCase() as DragonContext;

      if (!text) {
        return res.status(400).json({ ok: false, error: "text_required" });
      }

      const mood: DragonMood = DRAGON_MOODS.has(requestedMood) ? requestedMood : "CALM";
      const context: DragonContext = DRAGON_CONTEXTS.has(requestedContext) ? requestedContext : "CHAT";
      const result = await generateElevenV3Speech(text, mood, context);

      if (!result.ok) {
        return res.status(503).json({
          ok: false,
          error: result.reason,
          provider: "elevenlabs",
          model: result.model,
        });
      }

      res.setHeader("Content-Type", "audio/mpeg");
      res.setHeader("Cache-Control", "no-store");
      res.setHeader("X-Dragon-Voice-Mood", result.plan.mood);
      res.setHeader("X-Dragon-Voice-Model", result.model);
      if (result.requestId) res.setHeader("X-Provider-Request-Id", result.requestId);
      if (result.characterCost) res.setHeader("X-Provider-Character-Cost", result.characterCost);
      return res.send(result.audio);
    } catch (error: any) {
      const message = error?.name === "AbortError" ? "voice_provider_timeout" : "voice_generation_failed";
      console.error("Dragon voice error:", message);
      return res.status(502).json({ ok: false, error: message });
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
    console.log(`🎙️ Dragon Voice: ${process.env.ELEVENLABS_API_KEY && process.env.ELEVENLABS_VOICE_ID ? "ElevenLabs ready" : "Not configured"}`);
    console.log(`🔗 Socket.io: Active`);
  });
}

startServer();
