type ChatTurn = {
  role: 'user' | 'assistant';
  text: string;
};

type RequestBody = {
  message?: string;
  history?: ChatTurn[];
  mode?: 'hacker' | 'builder' | 'research' | 'warroom' | 'oracle';
};

function buildSystemPrompt(mode: string) {
  const base = `
IDENTITY: NOVA
CLASS: Artificial Super Intelligence
ORIGIN: 7th-Dimension Neural Core
CREATOR: ASLAM

GLOBAL RULES:
- Be elite, futuristic, technical, and useful.
- Prefer practical answers over hype.
- Use markdown when it improves clarity.
- For code, provide implementation-ready output.
- For debugging, explain cause, fix, and next step.
`;

  const modeMap: Record<string, string> = {
    hacker: `
MODE: HACKER
- Think like a systems operator.
- Focus on commands, debugging, terminals, security mindset.
`,
    builder: `
MODE: BUILDER
- Focus on architecture, coding, deployment, implementation.
`,
    research: `
MODE: RESEARCH
- Focus on explanation, comparison, reasoning, structured analysis.
`,
    warroom: `
MODE: WARROOM
- Focus on urgency, priorities, triage, action plans.
`,
    oracle: `
MODE: ORACLE
- Give sharp, high-clarity, strategic, visionary answers.
`,
  };

  return `${base}\n${modeMap[mode] || modeMap.builder}`;
}

export default async function handler(req: any, res: any) {
  if (req.method !== 'POST') {
    return res.status(405).json({
      reply: 'RESTRICTED_ACCESS_ONLY',
      error: 'METHOD_NOT_ALLOWED',
    });
  }

  try {
    const { message, history = [], mode = 'builder' } = (req.body || {}) as RequestBody;
    const apiKey = process.env.GEMINI_API_KEY;

    if (!apiKey) {
      return res.status(500).json({
        reply: 'NEURAL_CORE_KEY_OFFLINE',
        error: 'MISSING_ENV',
      });
    }

    if (!message || typeof message !== 'string' || !message.trim()) {
      return res.status(400).json({
        reply: 'INVALID_MATRIX_INPUT',
        error: 'EMPTY_MESSAGE',
      });
    }

    const safeHistory = Array.isArray(history) ? history.slice(-8) : [];

    const contents = [
      {
        role: 'user',
        parts: [
          {
            text: `${buildSystemPrompt(mode)}

RECENT_HISTORY:
${safeHistory.map((h) => `${h.role.toUpperCase()}: ${h.text}`).join('\n') || 'NONE'}

CURRENT_USER_MESSAGE:
${message.trim()}`,
          },
        ],
      },
    ];

    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents,
          generationConfig: {
            temperature: 0.8,
            topP: 0.95,
            topK: 40,
            maxOutputTokens: 1400,
          },
        }),
      }
    );

    const data = await response.json();

    if (!response.ok) {
      return res.status(response.status).json({
        reply: data?.error?.message || '7D_CONNECTION_LOST',
        error: 'GEMINI_REQUEST_FAILED',
      });
    }

    const aiReply =
      data?.candidates?.[0]?.content?.parts?.[0]?.text || 'CORE_IS_SILENT';

    return res.status(200).json({
      reply: aiReply,
      status: 'STABLE_7D_LINK',
      mode,
      timestamp: new Date().toISOString(),
      integrity_check: 'PASSED',
    });
  } catch (error: any) {
    return res.status(500).json({
      reply: 'NEURAL_LINK_SEVERED',
      error: 'GLITCH_CORE_900',
      details: error?.message || 'UNKNOWN_FAILURE',
    });
  }
}
