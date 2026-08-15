export type LocalDragonVoiceProfile =
  | 'nova_warm'
  | 'dragon_playful'
  | 'dragon_serious'
  | 'dragon_deep'
  | 'whatsapp_natural'
  | 'story_soul'
  | 'night_whisper';

export interface LocalDragonVoiceRequest {
  text: string;
  profile?: LocalDragonVoiceProfile;
  intensity?: number;
}

export interface LocalDragonVoiceResult {
  audio: Buffer;
  contentType: string;
  profile: string;
  model: string;
  modelFallback: boolean;
  inferenceMs: number | null;
}

export function localDragonVoiceConfigured(): boolean {
  return Boolean(process.env.DRAGON_LOCAL_VOICE_URL && process.env.DRAGON_LOCAL_VOICE_TOKEN);
}

export async function generateLocalDragonVoice(
  request: LocalDragonVoiceRequest,
): Promise<LocalDragonVoiceResult> {
  const baseUrl = (process.env.DRAGON_LOCAL_VOICE_URL || '').replace(/\/$/, '');
  const token = process.env.DRAGON_LOCAL_VOICE_TOKEN || '';

  if (!baseUrl || !token) {
    throw new Error('local_voice_not_configured');
  }

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 45_000);

  try {
    const response = await fetch(`${baseUrl}/v1/speak`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
        Accept: 'audio/wav',
      },
      body: JSON.stringify({
        text: request.text.slice(0, 1200),
        profile: request.profile ?? 'nova_warm',
        intensity: Math.max(0, Math.min(1, request.intensity ?? 0.65)),
      }),
      signal: controller.signal,
    });

    if (!response.ok) {
      const detail = (await response.text()).slice(0, 240);
      throw new Error(`local_voice_http_${response.status}:${detail}`);
    }

    const inferenceHeader = response.headers.get('x-dragon-inference-ms');
    const inferenceMs = inferenceHeader && /^\d+$/.test(inferenceHeader)
      ? Number(inferenceHeader)
      : null;

    return {
      audio: Buffer.from(await response.arrayBuffer()),
      contentType: response.headers.get('content-type') || 'audio/wav',
      profile: response.headers.get('x-dragon-voice-profile') || request.profile || 'nova_warm',
      model: response.headers.get('x-dragon-voice-model') || 'unknown',
      modelFallback: response.headers.get('x-dragon-model-fallback') === 'yes',
      inferenceMs,
    };
  } finally {
    clearTimeout(timeout);
  }
}
