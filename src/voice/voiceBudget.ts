export type DragonVoiceProvider = 'local' | 'openai' | 'elevenlabs';

export interface VoiceUsageState {
  date: string;
  requestCount: number;
  characterCount: number;
}

export interface VoiceBudgetLimits {
  maxRequests: number;
  maxCharacters: number;
}

export type VoiceBudgetReservation =
  | { allowed: true; next: VoiceUsageState }
  | {
      allowed: false;
      reason: 'voice_daily_request_limit' | 'voice_daily_character_limit';
      next: VoiceUsageState;
    };

const PROVIDERS = new Set<DragonVoiceProvider>(['local', 'openai', 'elevenlabs']);

function nonNegativeInteger(value: unknown): number {
  return typeof value === 'number' && Number.isFinite(value)
    ? Math.max(0, Math.floor(value))
    : 0;
}

export function parsePositiveInteger(value: string | undefined, fallback: number): number {
  const parsed = Number(value);
  if (!Number.isFinite(parsed) || parsed <= 0) return fallback;
  return Math.min(1_000_000, Math.floor(parsed));
}

export function resolveDragonVoiceProvider(value: string | undefined): DragonVoiceProvider {
  const candidate = value?.trim().toLowerCase() as DragonVoiceProvider | undefined;
  return candidate && PROVIDERS.has(candidate) ? candidate : 'local';
}

export function utcVoiceUsageDate(now = new Date()): string {
  return now.toISOString().slice(0, 10);
}

export function normalizeVoiceUsage(
  value: Partial<VoiceUsageState> | null | undefined,
  date: string,
): VoiceUsageState {
  if (value?.date !== date) {
    return { date, requestCount: 0, characterCount: 0 };
  }

  return {
    date,
    requestCount: nonNegativeInteger(value.requestCount),
    characterCount: nonNegativeInteger(value.characterCount),
  };
}

export function reserveVoiceBudget(
  current: VoiceUsageState,
  limits: VoiceBudgetLimits,
  inputCharacters: number,
): VoiceBudgetReservation {
  const characters = nonNegativeInteger(inputCharacters);

  if (current.requestCount >= limits.maxRequests) {
    return { allowed: false, reason: 'voice_daily_request_limit', next: current };
  }

  if (current.characterCount + characters > limits.maxCharacters) {
    return { allowed: false, reason: 'voice_daily_character_limit', next: current };
  }

  return {
    allowed: true,
    next: {
      ...current,
      requestCount: current.requestCount + 1,
      characterCount: current.characterCount + characters,
    },
  };
}
