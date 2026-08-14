import type { DragonMood, VoiceSoulPlan } from './voiceSoul';

export const DRAGON_VOICE_PROFILE_IDS = [
  'NOVA',
  'EVE',
  'DRAGON',
  'ANANYA',
  'GUARDIAN',
  'NARRATOR',
] as const;

export type DragonVoiceProfileId = (typeof DRAGON_VOICE_PROFILE_IDS)[number];

export interface DragonVoiceProfile {
  id: DragonVoiceProfileId;
  label: string;
  openaiVoice: 'alloy' | 'coral' | 'onyx' | 'sage' | 'marin' | 'cedar';
  baseInstructions: string;
}

const profiles: Record<DragonVoiceProfileId, DragonVoiceProfile> = {
  NOVA: {
    id: 'NOVA',
    label: 'NOVA',
    openaiVoice: 'marin',
    baseInstructions: 'Speak with a warm, clear, composed assistant voice.',
  },
  EVE: {
    id: 'EVE',
    label: 'EVE',
    openaiVoice: 'cedar',
    baseInstructions: 'Speak with a friendly, confident, helpful voice.',
  },
  DRAGON: {
    id: 'DRAGON',
    label: 'DRAGON',
    openaiVoice: 'onyx',
    baseInstructions: 'Speak with grounded, deliberate, protective authority.',
  },
  ANANYA: {
    id: 'ANANYA',
    label: 'ANANYA',
    openaiVoice: 'coral',
    baseInstructions: 'Speak with a bright, gentle, playful energy.',
  },
  GUARDIAN: {
    id: 'GUARDIAN',
    label: 'GUARDIAN',
    openaiVoice: 'sage',
    baseInstructions: 'Speak clearly, calmly, and firmly for safety guidance.',
  },
  NARRATOR: {
    id: 'NARRATOR',
    label: 'NARRATOR',
    openaiVoice: 'alloy',
    baseInstructions: 'Speak with a balanced, expressive storytelling voice.',
  },
};

const moodInstructions: Record<DragonMood, string> = {
  CALM: 'Use an even, reassuring pace.',
  PLAYFUL: 'Use light, upbeat energy without exaggeration.',
  CURIOUS: 'Use an engaged, thoughtful tone.',
  SERIOUS: 'Use a concise, steady, serious tone.',
  WHISPER: 'Use a soft, intimate, low-energy delivery.',
};

export function getDragonVoiceProfile(value?: string | null): DragonVoiceProfile {
  const candidate = value?.trim().toUpperCase() as DragonVoiceProfileId | undefined;
  const profile = candidate && candidate in profiles ? profiles[candidate] : profiles.NOVA;
  return { ...profile };
}

export function listDragonVoiceProfiles(): Array<Pick<DragonVoiceProfile, 'id' | 'label' | 'openaiVoice'>> {
  return DRAGON_VOICE_PROFILE_IDS.map((id) => {
    const { label, openaiVoice } = profiles[id];
    return { id, label, openaiVoice };
  });
}

export function buildOpenAITtsInstructions(
  plan: VoiceSoulPlan,
  profile: DragonVoiceProfile,
): string {
  return [
    profile.baseInstructions,
    moodInstructions[plan.mood],
    'Preserve the supplied wording. Do not add commentary or sound-effect labels.',
  ].join(' ');
}
