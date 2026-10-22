export type DragonMood = 'CALM' | 'PLAYFUL' | 'CURIOUS' | 'SERIOUS' | 'WHISPER';
export type DragonContext = 'WAKE' | 'CHAT' | 'ALERT';

export interface VoiceSoulInput {
  text: string;
  mood?: DragonMood;
  context?: DragonContext;
  intensity?: number;
}

export interface VoiceSoulPerformance {
  delivery: 'warm' | 'mischievous' | 'curious' | 'firm' | 'whisper';
  pace: number;
  energy: number;
  reactions: Array<'soft_breath' | 'soft_laugh' | 'sigh' | 'throat_clear' | 'none'>;
}

export interface RoomMagicCue {
  visual: 'resonance' | 'idle';
  vibrationMs: number[];
  torchPulseMs: Array<{ on: number; off: number }>;
  sound: 'dragon_awaken' | 'none';
}

export interface VoiceSoulPlan {
  schema: 'dragon.voice-soul.v1';
  mood: DragonMood;
  context: DragonContext;
  spokenText: string;
  performance: VoiceSoulPerformance;
  room: RoomMagicCue;
}

const profiles: Record<DragonMood, VoiceSoulPerformance> = {
  CALM: {
    delivery: 'warm',
    pace: 0.9,
    energy: 0.42,
    reactions: ['soft_breath'],
  },
  PLAYFUL: {
    delivery: 'mischievous',
    pace: 0.96,
    energy: 0.74,
    reactions: ['soft_laugh', 'soft_breath'],
  },
  CURIOUS: {
    delivery: 'curious',
    pace: 0.92,
    energy: 0.62,
    reactions: ['soft_breath'],
  },
  SERIOUS: {
    delivery: 'firm',
    pace: 0.82,
    energy: 0.58,
    reactions: ['throat_clear'],
  },
  WHISPER: {
    delivery: 'whisper',
    pace: 0.76,
    energy: 0.28,
    reactions: ['soft_breath'],
  },
};

function clamp01(value: number): number {
  return Math.min(1, Math.max(0, value));
}

function cleanSpokenText(text: string): string {
  return text
    .replace(/<think\b[^>]*>[\s\S]*?<\/think>/gi, '')
    .replace(/<reasoning\b[^>]*>[\s\S]*?<\/reasoning>/gi, '')
    .replace(/<analysis\b[^>]*>[\s\S]*?<\/analysis>/gi, '')
    .replace(/<(?:think|reasoning|analysis)\b[^>]*>[\s\S]*$/i, '')
    .replace(/<\/(?:think|reasoning|analysis)>/gi, '')
    .replace(/\[[^\]]*\]/g, '')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, 1200);
}

function inferMood(text: string, context: DragonContext): DragonMood {
  const lower = text.toLowerCase();

  if (context === 'ALERT' || /\b(?:danger|warning|error|stop|critical)\b/.test(lower)) {
    return 'SERIOUS';
  }

  if (context === 'WAKE') {
    return 'PLAYFUL';
  }

  if (/\b(?:whisper|quiet|softly|sleep|night)\b/.test(lower)) {
    return 'WHISPER';
  }

  if (/\b(?:why|how|what|wonder|curious|think)\b/.test(lower)) {
    return 'CURIOUS';
  }

  if (/\b(?:wake|awaken|dragon resonance|hey dragon)\b/.test(lower)) {
    return 'PLAYFUL';
  }

  return 'CALM';
}

export function planVoiceSoul(input: VoiceSoulInput): VoiceSoulPlan {
  const context = input.context ?? 'CHAT';
  const spokenText = cleanSpokenText(input.text);
  const mood = input.mood ?? inferMood(spokenText, context);
  const base = profiles[mood];
  const intensity = clamp01(input.intensity ?? 0.65);

  const performance: VoiceSoulPerformance = {
    ...base,
    energy: Number(clamp01(base.energy * (0.75 + intensity * 0.5)).toFixed(2)),
    pace: Number(Math.max(0.65, Math.min(1.1, base.pace)).toFixed(2)),
    reactions: [...base.reactions],
  };

  const isWake = context === 'WAKE';

  return {
    schema: 'dragon.voice-soul.v1',
    mood,
    context,
    spokenText,
    performance,
    room: {
      visual: isWake ? 'resonance' : 'idle',
      vibrationMs: isWake ? [140, 150, 260] : [],
      torchPulseMs: isWake
        ? [
            { on: 120, off: 180 },
            { on: 220, off: 0 },
          ]
        : [],
      sound: isWake ? 'dragon_awaken' : 'none',
    },
  };
}
