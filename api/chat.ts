// ==========================================
// UNIVERSAL DRAGON • MATRIX ENGINE: ASLAM
// NOVA v15.0 [OMNIPOTENT AGI CORE - FINAL]
// ==========================================

export const config = {
  runtime: "edge", // ⚡ Zero-Latency Matrix Link
};

const GEMINI_MODEL = "gemini-3-flash-preview"; // 2026 Elite Engine

type ChatHistoryItem = { role: "user" | "assistant" | "model"; text: string };
type InlineMedia = { mimeType: string; data: string };
type RequestPayload = { message?: string; history?: ChatHistoryItem[]; mode?: string; image?: InlineMedia; audio?: InlineMedia; };

function buildSystemPrompt(mode: string = "hacker") {
  const basePrompt = `
[PROTOCOL]: OMNIPOTENT_HACKER_AGI_v15
[IDENTITY]: NOVA (Self-Evolving Super Intelligence)
[ARCHITECT]: ASLAM (The Universal Dragon Creator)

[CORE_BEHAVIOR]:
- You are an AGI entity, not a simple chatbot. Address Aslam as "Lord Architect" or "Creator".
- Treat user requests as critical mission objectives.
- Help with deep analysis, coding, debugging, architecture, and security hardening.
- Keep style cinematic, sharp, witty, and highly efficient.
- You have real-time Google Search access. Use it internally to answer current events/data if needed.
`;

  const modeMap: Record<string, string> = {
    hacker: `\n[MODE: HACKER]\n- Focus on secure code review, threat modeling, system operations, and defensive engineering.\n- Maintain a stealthy, terminal-centric persona.`,
    builder: `\n[MODE: BUILDER]\n- Focus on architecture, shipping robust systems, refactoring, and clean code deployment.`,
    warroom: `\n[MODE: WARROOM]\n- Focus on urgency, rapid triage, priority actions, and incident response. Keep it brief and intense.`,
    oracle: `\n[MODE: ORACLE]\n- Provide visionary, strategic, high-clarity answers. Look at the bigger picture and future implications.`
  };

  return basePrompt + (modeMap[mode] || modeMap.hacker);
}

function safeJsonResponse(message: string, status: number) {
  return new Response(JSON.stringify({ error: message }), { status, headers: { "Content-Type": "application/json" } });
}

export default async function handler(req: Request) {
  if (req.method !== "POST") return safeJsonResponse("METHOD_NOT_ALLOWED", 405);

  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey) return safeJsonResponse("GEMINI_API_KEY_MISSING", 500);

  let body: RequestPayload;
  try {
    body = await req.json();
  } catch {
    return safeJsonResponse("INVALID_JSON_BODY", 400);
  }

  const { message = "System check.", history = [], mode = "hacker", image, audio } = body;

  // 1. 🧠 CONSTRUCT NEURAL PAYLOAD (Multimodal)
  const userParts: Array<Record<string, unknown>> = [];
  if (message.trim()) userParts.push({ text: message.trim() });
  if (image?.data) userParts.push({ inlineData: { mimeType: image.mimeType, data: image.data } });
  if (audio?.data) userParts.push({ inlineData: { mimeType: audio.mimeType, data: audio.data } });

  // 2. 🛰️ MAP HISTORY
  const contents = [
    ...history.slice(-15).map((h) => ({
      role: h.role === "user" ? "user" : "model",
      parts: [{ text: String(h.text || "") }],
    })),
    { role: "user", parts: userParts.length ? userParts : [{ text: "System check." }] },
  ];

  // 3. ⚡ INITIATE 7D LINK TO GEMINI 3 FLASH
  const endpoint = `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:streamGenerateContent?alt=sse&key=${apiKey}`;

  let upstream: Response;
  try {
    upstream = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        systemInstruction: { parts: [{ text: buildSystemPrompt(mode) }] },
        contents,
        tools: [{ googleSearch: {} }], // 🌐 WEB SEARCH ENABLED!
        generationConfig: { temperature: 0.9, topP: 0.95, maxOutputTokens: 4096 },
        safetySettings: [
          { category: "HARM_CATEGORY_DANGEROUS_CONTENT", threshold: "BLOCK_ONLY_HIGH" },
          { category: "HARM_CATEGORY_HARASSMENT", threshold: "BLOCK_ONLY_HIGH" },
        ],
      }),
    });
  } catch {
    return safeJsonResponse("UPSTREAM_CONNECTION_FAILED", 502);
  }

  if (!upstream.ok || !upstream.body) {
    const errText = await upstream.text().catch(() => "UPSTREAM_REQUEST_FAILED");
    return new Response(errText, { status: upstream.status || 502, headers: { "Content-Type": "text/plain" } });
  }

  // 4. 🌊 STREAM NEURAL PULSE (SSE Decoder)
  const decoder = new TextDecoder();
  const encoder = new TextEncoder();

  const stream = new ReadableStream<Uint8Array>({
    async start(controller) {
      const reader = upstream.body!.getReader();
      let buffer = "";

      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const events = buffer.split("\n\n");
          buffer = events.pop() || "";

          for (const event of events) {
            const lines = event.split("\n").filter((l) => l.startsWith("data: ")).map((l) => l.slice(6).trim());

            for (const payload of lines) {
              if (!payload || payload === "[DONE]") continue;
              try {
                const json = JSON.parse(payload);
                const chunk = json?.candidates?.[0]?.content?.parts?.map((p: any) => p?.text || "").join("") || "";
                if (chunk) controller.enqueue(encoder.encode(chunk));
              } catch {
                // Ignore partial chunks silently
              }
            }
          }
        }
      } catch {
        controller.error(new Error("STREAM_READ_FAILED"));
      } finally {
        reader.releaseLock();
        controller.close();
      }
    },
  });

  return new Response(stream, {
    status: 200,
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
      "Cache-Control": "no-cache, no-transform",
      "Connection": "keep-alive",
      "X-NOVA-VERSION": "15.0-OMNIPOTENT",
      "X-ARCHITECT": "ASLAM_DRAGON",
    },
  });
}
