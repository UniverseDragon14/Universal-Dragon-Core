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

const eleven = renderElevenV3Prompt(wake);
assert.ok(eleven.includes('[mischievously]'));
assert.ok(eleven.includes('[laughs softly]'));
assert.ok(eleven.includes('Hey Dragon, awaken.'));
assert.ok(!eleven.includes('<think>'));

console.log('VOICE_SOUL_SCHEMA=PASS');
console.log('VOICE_SOUL_SANITIZER=PASS');
console.log('VOICE_SOUL_ROOM_CUES=PASS');
console.log('ELEVEN_V3_RENDERER=PASS');
console.log('DRAGON_VOICE_SOUL_V1=PASS');
