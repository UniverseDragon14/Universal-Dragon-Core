import type { VoiceSoulPlan } from './voiceSoul';

const deliveryTags: Record<VoiceSoulPlan['performance']['delivery'], string> = {
  warm: '[warmly]',
  mischievous: '[mischievously]',
  curious: '[curious]',
  firm: '[firmly]',
  whisper: '[whispers]',
};

const reactionTags: Record<VoiceSoulPlan['performance']['reactions'][number], string> = {
  soft_breath: '[sighs]',
  soft_laugh: '[laughs softly]',
  sigh: '[sighs]',
  throat_clear: '[clears throat]',
  none: '',
};

/**
 * Render a provider-neutral Voice Soul plan into Eleven v3 prompt text.
 *
 * This function does not call ElevenLabs and never handles credentials.
 * Provider/network execution belongs in a server-side adapter.
 */
export function renderElevenV3Prompt(plan: VoiceSoulPlan): string {
  const delivery = deliveryTags[plan.performance.delivery];
  const reactions = plan.performance.reactions
    .map((reaction) => reactionTags[reaction])
    .filter(Boolean);

  const opening = reactions[0] ? `${reactions[0]} ` : '';
  const closing = reactions.length > 1 ? ` ${reactions.slice(1).join(' ')}` : '';

  return `${delivery} ${opening}${plan.spokenText}${closing}`
    .replace(/\s+/g, ' ')
    .trim();
}
