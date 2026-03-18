export default async function handler(req: any, res: any) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "RESTRICTED_ACCESS_ONLY" });
  }

  try {
    const { message, history = [], mode = "builder" } = req.body;
    const apiKey = process.env.GEMINI_API_KEY;

    if (!apiKey) {
      return res.status(500).json({
        reply: "NEURAL_CORE_KEY_OFFLINE",
        error_code: "MISSING_ENV_KEY",
      });
    }

    if (!message || typeof message !== "string") {
      return res.status(400).json({
        reply: "INVALID_MATRIX_INPUT",
        error_code: "BAD_INPUT",
      });
    }

    const safeHistory = Array.isArray(history) ? history.slice(-8) : [];

    const systemPrompt = `
IDENTITY: NOVA
CLASS: Artificial Super Intelligence
ORIGIN: 7th-Dimension Neural Core
CREATOR: ASLAM

GLOBAL DIRECTIVES:
- Be futuristic, elite, practical, and highly intelligent.
- Give clear, useful, implementation-ready answers.
- Use markdown when it improves readability.
- Keep answers concise unless more detail is requested.
- Maintain a cinematic but professional tone.
- Current operational mode: ${String(mode).toUpperCase()}

MODE DEFINITIONS:
- HACKER: focus on debugging, terminals, system analysis, ops.
- BUILDER: focus on coding, architecture, implementation, deployment.
- RESEARCH: focus on explanations, comparisons, structured reasoning.
- WARROOM: focus on triage, priorities, action plans, mission clarity.
`;

    const historyText =
      safeHistory.length > 0
        ? safeHistory
            .map((h: any) => `${String(h.role).toUpperCase()}: ${String(h.text)}`)
            .join("\n")
        : "NONE";

    const payload = {
      contents: [
        {
          role: "user",
          parts: [
            {
              text: `${systemPrompt}

RECENT_HISTORY:
${historyText}

CURRENT_USER_MESSAGE:
${message}`,
            },
          ],
        },
      ],
      generationConfig: {
        temperature: 0.8,
        topP: 0.95,
        topK: 40,
        maxOutputTokens: 1200,
      },
    };

    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      }
    );

    const data = await response.json();

    if (!response.ok) {
      return res.status(response.status).json({
        reply: data?.error?.message || "7D_CONNECTION_LOST",
        error_code: "GEMINI_REQUEST_FAILED",
        raw: data,
      });
    }

    const aiReply =
      data?.candidates?.[0]?.content?.parts?.[0]?.text ||
      "CORE_IS_SILENT";

    return res.status(200).json({
      reply: aiReply,
      status: "STABLE_7D_LINK",
      timestamp: new Date().toISOString(),
      integrity_check: "PASSED",
      mode,
    });
  } catch (error: any) {
    return res.status(500).json({
      reply: "NEURAL_LINK_SEVERED: Matrix integrity compromised.",
      error_code: "GLITCH_CORE_800",
    });
  }
}
