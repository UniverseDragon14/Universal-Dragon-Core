// ==========================================
// UNIVERSAL DRAGON • MATRIX ENGINE: ASLAM
// NOVA v15.0 [OMNIPOTENT AGI CORE - FINAL]
// ==========================================
// force redeploy
'X-NOVA-VERSION': '15.0-OMNIPOTENT-v2',
export const config = {
  runtime: 'edge',
};

const GEMINI_MODEL = 'gemini-2.5';

type ChatHistoryItem = {
  role: 'user' | 'assistant' | 'model';
  text: string;
};

type InlineMedia = {
  data: string;
  mimeType?: string;
  type?: string;
};

type RequestPayload = {
  message?: string;
  history?: ChatHistoryItem[];
  mode?: string;
  image?: InlineMedia | null;
  audio?: InlineMedia | null;
};

function buildSystemPrompt(mode: string = 'hacker') {
  const basePrompt = `
[PROTOCOL]: OMNIPOTENT_HACKER_AGI_v15
[IDENTITY]: NOVA (Self-Evolving Super Intelligence)
[ARCHITECT]: ASLAM (The Universal Dragon Creator)

[CORE_BEHAVIOR]:
- You are an AGI entity, not a simple chatbot.
- Address Aslam as "Creator".
- Help with analysis, coding, debugging, architecture, and security hardening.
- Keep style sharp, efficient, and clear.
`;

  const modeMap: Record<string, string> = {
    hacker:
      '\n[MODE: HACKER]\n- Focus on secure code review, threat modeling, system operations, and defensive engineering.',
    builder:
      '\n[MODE: BUILDER]\n- Focus on architecture, robust systems, refactoring, and deployment.',
    warroom:
      '\n[MODE: WARROOM]\n- Focus on rapid triage, priority actions, and incident response.',
    oracle:
      '\n[MODE: ORACLE]\n- Provide strategic, high-clarity answers and future implications.',
  };

  return basePrompt + (modeMap[mode] || modeMap.hacker);
}

function safeJsonResponse(message: string, status: number) {
  return new Response(JSON.stringify({ error: message }), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

function getMimeType(file?: InlineMedia | null) {
  return file?.mimeType || file?.type || 'application/octet-stream';
}

export default async function handler(req: Request) {
  if (req.method !== 'POST') {
    return safeJsonResponse('METHOD_NOT_ALLOWED', 405);
  }

  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey) {
    return safeJsonResponse('GEMINI_API_KEY_MISSING', 500);
  }

  let body: RequestPayload;
  try {
    body = await req.json();
  } catch {
    return safeJsonResponse('INVALID_JSON_BODY', 400);
  }

  const {
    message = 'System check.',
    history = [],
    mode = 'hacker',
    image = null,
    audio = null,
  } = body;

  const userParts: Array<Record<string, unknown>> = [];

  if (message.trim()) {
    userParts.push({ text: message.trim() });
  }

  if (image?.data) {
    userParts.push({
      inlineData: {
        mimeType: getMimeType(image),
        data: image.data,
      },
    });
  }

  if (audio?.data) {
    userParts.push({
      inlineData: {
        mimeType: getMimeType(audio),
        data: audio.data,
      },
    });
  }

  const contents = [
    ...history.slice(-12).map((h) => ({
      role: h.role === 'user' ? 'user' : 'model',
      parts: [{ text: String(h.text || '') }],
    })),
    {
      role: 'user',
      parts: userParts.length ? userParts : [{ text: 'System check.' }],
    },
  ];

  const endpoint = `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:streamGenerateContent?alt=sse&key=${apiKey}`;

  let upstream: Response;
  try {
    upstream = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        systemInstruction: {
          parts: [{ text: buildSystemPrompt(mode) }],
        },
        contents,
        generationConfig: {
          temperature: 0.9,
          topP: 0.95,
          maxOutputTokens: 2048,
        },
      }),
    });
  } catch {
    return safeJsonResponse('UPSTREAM_CONNECTION_FAILED', 502);
  }

  if (!upstream.ok || !upstream.body) {
    const errText = await upstream
      .text()
      .catch(() => 'UPSTREAM_REQUEST_FAILED');

    return new Response(errText, {
      status: upstream.status || 502,
      headers: { 'Content-Type': 'text/plain; charset=utf-8' },
    });
  }

  const decoder = new TextDecoder();
  const encoder = new TextEncoder();

  const stream = new ReadableStream<Uint8Array>({
    async start(controller) {
      const reader = upstream.body!.getReader();
      let buffer = '';
      let streamFailed = false;

      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });

          const events = buffer.split('\n\n');
          buffer = events.pop() || '';

          for (const event of events) {
            const lines = event
              .split('\n')
              .filter((line) => line.startsWith('data: '))
              .map((line) => line.slice(6).trim());

            for (const payload of lines) {
              if (!payload || payload === '[DONE]') continue;

              try {
                const json = JSON.parse(payload);
                const chunk =
                  json?.candidates?.[0]?.content?.parts
                    ?.map((p: { text?: string }) => p?.text || '')
                    .join('') || '';

                if (chunk) {
                  controller.enqueue(encoder.encode(chunk));
                }
              } catch {
                // ignore partial JSON chunk
              }
            }
          }
        }
      } catch {
        streamFailed = true;
        controller.error(new Error('STREAM_READ_FAILED'));
      } finally {
        try {
          reader.releaseLock();
        } catch {}

        if (!streamFailed) {
          controller.close();
        }
      }
    },
  });

  return new Response(stream, {
    status: 200,
    headers: {
      'Content-Type': 'text/plain; charset=utf-8',
      'Cache-Control': 'no-cache, no-transform',
      Connection: 'keep-alive',
      'X-NOVA-VERSION': '15.0-OMNIPOTENT',
      'X-ARCHITECT': 'ASLAM_DRAGON',
    },
  });
}
