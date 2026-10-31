import express from "express";
import { createServer as createViteServer } from "vite";
import { Server } from "socket.io";
import http from "http";
import mqtt from "mqtt";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function startServer() {
  const app = express();
  const server = http.createServer(app);
  const io = new Server(server);
  const PORT = 3000;

  // MQTT Integration
  const MQTT_BROKER = "mqtt://192.168.70.196"; // From user script
  const MQTT_TOPIC = "UniversalDragon/NOVA/Reply";

  const mqttClient = mqtt.connect(MQTT_BROKER, {
    connectTimeout: 15000, // Increased timeout for cloud-to-local attempts
    reconnectPeriod: 30000, // Slower reconnect to reduce log noise
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
      console.warn(`📡 MQTT Timeout: Broker at ${MQTT_BROKER} is unreachable from this cloud environment. (This is expected for local network IPs)`);
    } else {
      console.warn("⚠️ MQTT Connection Error:", err.message);
    }
    io.emit("mqtt_status", { connected: false, error: err.message, broker: MQTT_BROKER });
  });

  mqttClient.on("offline", () => {
    io.emit("mqtt_status", { connected: false, status: "offline" });
  });

  // API routes
  app.get("/api/health", (req, res) => {
    res.json({ status: "ok", mqtt: mqttClient.connected });
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
    console.log(`🔗 Socket.io: Active`);
  });
}

startServer();
