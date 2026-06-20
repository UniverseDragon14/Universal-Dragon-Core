import express from "express";
import { createServer as createViteServer } from "vite";
import { Server } from "socket.io";
import http from "http";
import mqtt from "mqtt";
import path from "path";
import { fileURLToPath } from "url";

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

async function startServer() {
  const app = express();
  const server = http.createServer(app);
  const io = new Server(server);
  const PORT = Number(process.env.PORT || 3000);

  app.use(express.json({ limit: "1mb" }));

  // MQTT Integration
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
      model: process.env.GROQ_API_KEY ? (process.env.GROQ_MODEL || "openai/gpt-oss-120b") : (process.env.OPENAI_MODEL || "gpt-4.1-mini")
    });
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

  // Vite middleware for development
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
    console.log(`🔗 Socket.io: Active`);
  });
}

startServer();
