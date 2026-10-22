import { strict as assert } from 'node:assert';
import { planVoiceSoul } from '../src/voice/voiceSoul';
import { renderElevenV3Prompt } from '../src/voice/elevenV3';

const wake = planVoiceSoul({
  context: 'WAKE',
  text: 'Hey Dragon, awaken.',
  mood: 'PLAYFUL',
});

assert.equal(wake.schema, 'dragon.voice-soul.v1');
assert.equal(wake.mood, 'PLAYFUL');
assert.equal(wake.room.visual, 'resonance');
assert.equal(wake.room.sound, 'dragon_awaken');
assert.deepEqual(wake.room.vibrationMs, [140, 150, 260]);
assert.equal(wake.room.torchPulseMs.length, 2);
assert.ok(wake.performance.energy >= 0 && wake.performance.energy <= 1);

const sanitized = planVoiceSoul({
  context: 'CHAT',
  text: '<think>private chain</think> Hello [laughs] friend.',
  mood: 'CALM',
});

assert.equal(sanitized.spokenText, 'Hello friend.');
assert.equal(sanitized.room.visual, 'idle');
assert.equal(sanitized.room.torchPulseMs.length, 0);

const truncatedReasoning = planVoiceSoul({
  context: 'CHAT',
  text: 'Safe answer. <reasoning>private unfinished chain',
  mood: 'CALM',
});
assert.equal(truncatedReasoning.spokenText, 'Safe answer.');

const longInjectedTag = `[${'x'.repeat(80)}]`;
const strippedLongTag = planVoiceSoul({
  context: 'CHAT',
  text: `Hello ${longInjectedTag} friend.`,
  mood: 'CALM',
});
assert.equal(strippedLongTag.spokenText, 'Hello friend.');

const ordinaryStatus = planVoiceSoul({
  context: 'CHAT',
  text: 'Show me the status of the unstoppable process.',
});
assert.equal(ordinaryStatus.mood, 'CALM');

const wakePriority = planVoiceSoul({
  context: 'WAKE',
  text: 'What did you say?',
});
assert.equal(wakePriority.mood, 'PLAYFUL');

const alertPriority = planVoiceSoul({
  context: 'ALERT',
  text: 'Hey Dragon, wake up.',
});
assert.equal(alertPriority.mood, 'SERIOUS');

const eleven = renderElevenV3Prompt(wake);
assert.ok(eleven.includes('[mischievously]'));
assert.ok(eleven.includes('[laughs softly]'));
assert.ok(eleven.includes('[exhales]'));
assert.ok(eleven.includes('Hey Dragon, awaken.'));
assert.ok(!eleven.includes('<think>'));

console.log('VOICE_SOUL_SCHEMA=PASS');
console.log('VOICE_SOUL_SANITIZER=PASS');
console.log('VOICE_SOUL_TRUNCATED_REASONING=PASS');
console.log('VOICE_SOUL_TAG_INJECTION=PASS');
console.log('VOICE_SOUL_MOOD_BOUNDARIES=PASS');
console.log('VOICE_SOUL_CONTEXT_PRIORITY=PASS');
console.log('VOICE_SOUL_ROOM_CUES=PASS');
console.log('ELEVEN_V3_RENDERER=PASS');
console.log('DRAGON_VOICE_SOUL_V1=PASS');
