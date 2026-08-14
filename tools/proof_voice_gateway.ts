import { strict as assert } from 'node:assert';
import {
  buildOpenAITtsInstructions,
  getDragonVoiceProfile,
  listDragonVoiceProfiles,
} from '../src/voice/openaiTts';
import {
  normalizeVoiceUsage,
  parsePositiveInteger,
  reserveVoiceBudget,
  resolveDragonVoiceProvider,
} from '../src/voice/voiceBudget';
import { planVoiceSoul } from '../src/voice/voiceSoul';

const profiles = listDragonVoiceProfiles();
assert.equal(profiles.length, 6);
assert.deepEqual(
  profiles.map((profile) => profile.id),
  ['NOVA', 'EVE', 'DRAGON', 'ANANYA', 'GUARDIAN', 'NARRATOR'],
);
assert.equal(getDragonVoiceProfile('eve').openaiVoice, 'cedar');
assert.equal(getDragonVoiceProfile('unknown').id, 'NOVA');

const plan = planVoiceSoul({
  context: 'WAKE',
  text: 'Dragon Resonance active.',
  mood: 'PLAYFUL',
});
const instructions = buildOpenAITtsInstructions(plan, getDragonVoiceProfile('NOVA'));
assert.ok(instructions.includes('warm, clear, composed'));
assert.ok(instructions.includes('upbeat energy'));

assert.equal(resolveDragonVoiceProvider('openai'), 'openai');
assert.equal(resolveDragonVoiceProvider('invalid'), 'local');
assert.equal(parsePositiveInteger('0', 6), 6);
assert.equal(parsePositiveInteger('12', 6), 12);

const current = normalizeVoiceUsage(
  { date: '2026-08-14', requestCount: 5, characterCount: 2_000 },
  '2026-08-14',
);
const accepted = reserveVoiceBudget(current, { maxRequests: 6, maxCharacters: 2_400 }, 400);
assert.equal(accepted.allowed, true);
if (!accepted.allowed) {
  throw new Error('Expected accepted voice budget reservation');
}
assert.equal(accepted.next.requestCount, 6);
assert.equal(accepted.next.characterCount, 2_400);

const blockedByRequests = reserveVoiceBudget(
  accepted.next,
  { maxRequests: 6, maxCharacters: 2_400 },
  1,
);
assert.deepEqual(blockedByRequests, {
  allowed: false,
  reason: 'voice_daily_request_limit',
  next: accepted.next,
});

const blockedByCharacters = reserveVoiceBudget(
  { date: '2026-08-14', requestCount: 1, characterCount: 2_300 },
  { maxRequests: 6, maxCharacters: 2_400 },
  101,
);
assert.equal(blockedByCharacters.allowed, false);
if (blockedByCharacters.allowed === false) {
  assert.equal(blockedByCharacters.reason, 'voice_daily_character_limit');
}

console.log('OPENAI_VOICE_PROFILES=PASS');
console.log('VOICE_BUDGET_GUARD=PASS');
console.log('DRAGON_VOICE_GATEWAY=PASS');
