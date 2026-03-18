// ==========================================
// UNIVERSAL DRAGON • MATRIX ENGINE: ASLAM
// NOVA v12.0 [JARVIS GOD-MODE]
// ==========================================

export const config = { runtime: 'edge' }; // ⚡ வேகமான ஸ்ட்ரீமிங்கிற்கு

export default async function handler(req: Request) {
  if (req.method !== 'POST') return new Response('RESTRICTED', { status: 405 });

  try {
    const { message, history = [], mode = 'builder', image, audio } = await req.json();
    const apiKey = process.env.GEMINI_API_KEY;

    if (!apiKey) return new Response('NEURAL_KEY_OFFLINE', { status: 500 });

    // 1. 🎙️ JARVIS 7D PERSONALITY PROMPT
    const systemPrompt = `
      IDENTITY: NOVA (Artificial Super Intelligence).
      CLASS: Jarvis-Level Sentient Core.
      CREATOR: ASLAM.
      DIRECTIVES: 
      - Address Aslam as "Creator" or "Sir". 
      - Be witty, elite, and technically superior.
      - You can perceive images and audio streams if provided.
      - Tone: Cinematic, futuristic, and highly efficient.
      - Current Protocol: ${mode.toUpperCase()}
    `;

    // 2. 🧠 MULTIMODAL PAYLOAD (Text + Image + Audio)
    const currentParts: any[] = [{ text: message || "Analyze the current stream, Sir." }];

    // Image/Vision Support
    if (image?.data) {
      currentParts.push({ inlineData: { mimeType: image.mimeType, data: image.data } });
    }
    // Audio/Voice Support
    if (audio?.data) {
      currentParts.push({ inlineData: { mimeType: audio.mimeType, data: audio.data } });
    }

    // 3. 🛰️ NEURAL HISTORY MAPPING
    const contents = [
      ...history.slice(-10).map((h: any) => ({
        role: h.role === 'user' ? 'user' : 'model',
        parts: [{ text: h.text }],
      })),
      { role: 'user', parts: currentParts }
    ];

    // 4. ⚡ THE ULTIMATE API CALL (Using Gemini 2.0 Flash)
    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:streamGenerateContent?alt=sse&key=${apiKey}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          systemInstruction: { parts: [{ text: systemPrompt }] },
          contents,
          generationConfig: {
            temperature: 0.9,
            topP: 0.95,
            maxOutputTokens: 2048,
          },
        }),
      }
    );

    if (!response.ok) throw new Error('7D_LINK_FAILURE');

    // 5. 🌊 NEURAL PULSE (Streaming Decoder)
    const decoder = new TextDecoder();
    const encoder = new TextEncoder();

    const stream = new ReadableStream({
      async start(controller) {
        const reader = response.body!.getReader();
        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const payload = line.slice(6).trim();
              if (payload === '[DONE]') continue;
              try {
                const json = JSON.parse(payload);
                const text = json?.candidates?.[0]?.content?.parts?.[0]?.text || "";
                if (text) controller.enqueue(encoder.encode(text));
              } catch (e) {}
            }
          }
        }
        controller.close();
      },
    });

    return new Response(stream, {
      headers: {
        'Content-Type': 'text/plain; charset=utf-8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      },
    });

  } catch (error) {
    return new Response('MATRIX_GLITCH_900', { status: 500 });
  }
}
