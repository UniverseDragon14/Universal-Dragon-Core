export const runtime = 'edge';

function headers() {
  return {
    'Content-Type': 'text/plain; charset=utf-8',
    'Cache-Control': 'no-cache, no-transform',
    Connection: 'keep-alive',
  };
}

export async function POST(req: Request) {
  try {
    const { message, history = [], mode = 'builder', image } = await req.json();
    const apiKey = process.env.GEMINI_API_KEY;

    if (!apiKey || !message?.trim()) {
      return new Response('INVALID_INPUT', { status: 400 });
    }

    const userParts: any[] = [{ text: message.trim() }];

    if (image?.data && image?.mime_type) {
      userParts.push({
        inlineData: {
          mimeType: image.mime_type,
          data: image.data,
        },
      });
    }

    const contents = [
      ...history.slice(-8).map((h: any) => ({
        role: h.role === 'user' ? 'user' : 'model',
        parts: [{ text: h.text }],
      })),
      { role: 'user', parts: userParts },
    ];

    const geminiRes = await fetch(
      'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:streamGenerateContent?alt=sse',
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-goog-api-key': apiKey,
        },
        body: JSON.stringify({
          systemInstruction: {
            parts: [{
              text: `IDENTITY: NOVA. MODE: ${mode.toUpperCase()}. Style: Elite, technical.`,
            }],
          },
          contents,
          generationConfig: {
            temperature: 0.8,
            maxOutputTokens: 2048,
            mediaResolution: 'MEDIA_RESOLUTION_UNSPECIFIED',
          },
        }),
      }
    );

    if (!geminiRes.body) {
      return new Response('STREAM_FAIL', { status: 500 });
    }

    const decoder = new TextDecoder();
    const encoder = new TextEncoder();

    const stream = new ReadableStream({
      async start(controller) {
        const reader = geminiRes.body!.getReader();
        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });

          const events = buffer.split('\n\n');
          buffer = events.pop() || '';

          for (const event of events) {
            const lines = event.split('\n');

            for (const line of lines) {
              if (!line.startsWith('data: ')) continue;

              const payload = line.slice(6).trim();
              if (!payload || payload === '[DONE]') continue;

              try {
                const json = JSON.parse(payload);
                const text =
                  json?.candidates?.[0]?.content?.parts?.[0]?.text || '';

                if (text) {
                  controller.enqueue(encoder.encode(text));
                }
              } catch {}
            }
          }
        }

        controller.close();
      },
    });

    return new Response(stream, { headers: headers() });

  } catch {
    return new Response('ERROR', { status: 500 });
  }
}
