import React, { useEffect, useMemo, useRef, useState } from 'react';
import { AnimatePresence, motion, useReducedMotion } from 'motion/react';
import { Mic, Sparkles, Volume2, X } from 'lucide-react';
import { planVoiceSoul, type DragonMood } from '../voice/voiceSoul';
import { renderElevenV3Prompt } from '../voice/elevenV3';

interface DragonResonanceProps {
  open: boolean;
  onClose: () => void;
}

const moods: DragonMood[] = ['CALM', 'PLAYFUL', 'CURIOUS', 'SERIOUS', 'WHISPER'];

const particleSeeds = Array.from({ length: 34 }, (_, index) => ({
  id: index,
  angle: (index * 137.508) % 360,
  radius: 31 + ((index * 17) % 34),
  delay: (index % 9) * 0.12,
  duration: 2.8 + (index % 7) * 0.22,
  length: 10 + (index % 5) * 5,
}));

export const DragonResonance: React.FC<DragonResonanceProps> = ({ open, onClose }) => {
  const [mood, setMood] = useState<DragonMood>('PLAYFUL');
  const [awakened, setAwakened] = useState(false);
  const reduceMotion = Boolean(useReducedMotion());
  const dialogRef = useRef<HTMLElement>(null);
  const closeRef = useRef<HTMLButtonElement>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);
  const onCloseRef = useRef(onClose);

  useEffect(() => {
    onCloseRef.current = onClose;
  }, [onClose]);

  useEffect(() => {
    if (!open) {
      setAwakened(false);
      return;
    }

    previousFocusRef.current = document.activeElement instanceof HTMLElement
      ? document.activeElement
      : null;

    const focusTimer = window.setTimeout(() => closeRef.current?.focus(), 0);

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        event.preventDefault();
        onCloseRef.current();
        return;
      }

      if (event.key !== 'Tab') return;

      const dialog = dialogRef.current;
      if (!dialog) {
        event.preventDefault();
        return;
      }

      const focusable: HTMLElement[] = Array.from(
        dialog.querySelectorAll<HTMLElement>(
          'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])',
        ),
      ).filter((element) => element.offsetParent !== null);

      if (focusable.length === 0) {
        event.preventDefault();
        return;
      }

      const first: HTMLElement = focusable[0];
      const last: HTMLElement = focusable[focusable.length - 1];
      const active = document.activeElement;

      if (event.shiftKey && active === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && active === last) {
        event.preventDefault();
        first.focus();
      }
    };

    window.addEventListener('keydown', onKeyDown);

    return () => {
      window.clearTimeout(focusTimer);
      window.removeEventListener('keydown', onKeyDown);
      const previous = previousFocusRef.current;
      if (previous?.isConnected) previous.focus();
    };
  }, [open]);

  const plan = useMemo(
    () =>
      planVoiceSoul({
        context: 'WAKE',
        mood,
        intensity: awakened ? 0.9 : 0.65,
        text: 'Heey, Aslam... you really woke me up again. Dragon Resonance is active.',
      }),
    [awakened, mood],
  );

  const elevenPreview = useMemo(() => renderElevenV3Prompt(plan), [plan]);
  const renderedParticles = reduceMotion ? particleSeeds.slice(0, 12) : particleSeeds;

  const awaken = () => {
    const activePlan = planVoiceSoul({
      context: 'WAKE',
      mood,
      intensity: 0.9,
      text: 'Heey, Aslam... you really woke me up again. Dragon Resonance is active.',
    });

    setAwakened(true);
    window.dispatchEvent(
      new CustomEvent('DRAGON_ROOM_MAGIC_PREVIEW', {
        detail: activePlan,
      }),
    );
  };

  return (
    <AnimatePresence>
      {open && (
        <motion.section
          ref={dialogRef}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-[100] overflow-y-auto overflow-x-hidden bg-black text-white"
          role="dialog"
          aria-modal="true"
          aria-label="Dragon Resonance"
        >
          <div className="fixed inset-0 bg-[radial-gradient(circle_at_50%_42%,rgba(125,170,220,0.16),transparent_28%),radial-gradient(circle_at_50%_50%,rgba(255,255,255,0.04),transparent_48%)]" />

          <button
            ref={closeRef}
            type="button"
            onClick={onClose}
            className="fixed right-4 top-4 z-20 rounded-full border border-white/15 bg-black/50 p-2 text-white/70 backdrop-blur-md transition hover:bg-white/10 hover:text-white focus:outline-none focus:ring-2 focus:ring-slate-200/60"
            aria-label="Close Dragon Resonance"
          >
            <X className="h-5 w-5" />
          </button>

          <div className="relative flex min-h-full flex-col items-center justify-between gap-4 px-5 py-8 md:px-8">
            <header className="z-10 flex w-full max-w-3xl flex-none items-center justify-between pr-12 text-[10px] font-mono uppercase tracking-[0.22em] text-white/35">
              <span>Universal Dragon</span>
              <span>{awakened ? 'Resonance Active' : 'Room Magic Preview'}</span>
            </header>

            <div className="relative flex h-[clamp(220px,55vh,560px)] w-full max-w-[680px] flex-none items-center justify-center">
              <motion.div
                animate={reduceMotion ? { rotate: 0 } : { rotate: 360 }}
                transition={reduceMotion ? undefined : { repeat: Infinity, duration: awakened ? 18 : 28, ease: 'linear' }}
                className="absolute aspect-square w-[82%] rounded-full border border-white/[0.03]"
              />

              {Array.from({ length: 8 }, (_, index) => (
                <motion.div
                  key={index}
                  animate={
                    reduceMotion
                      ? { rotate: 0, scale: 1 }
                      : {
                          rotate: index % 2 === 0 ? 360 : -360,
                          scale: awakened ? [1, 1.025, 1] : 1,
                        }
                  }
                  transition={
                    reduceMotion
                      ? undefined
                      : {
                          rotate: {
                            repeat: Infinity,
                            duration: 16 + index * 3.5,
                            ease: 'linear',
                          },
                          scale: {
                            repeat: Infinity,
                            duration: 2.6 + index * 0.16,
                            ease: 'easeInOut',
                          },
                        }
                  }
                  className="absolute aspect-square rounded-full border border-slate-200/70 shadow-[0_0_22px_rgba(180,215,255,0.08)]"
                  style={{ width: `${29 + index * 6.8}%` }}
                />
              ))}

              {renderedParticles.map((particle) => {
                const rad = (particle.angle * Math.PI) / 180;
                const x = Math.cos(rad) * particle.radius;
                const y = Math.sin(rad) * particle.radius;

                return (
                  <div
                    key={particle.id}
                    className="absolute left-1/2 top-1/2"
                    style={{ transform: `translate(${x}vw, ${y}vw) rotate(${particle.angle + 88}deg)` }}
                  >
                    <motion.div
                      className="h-[3px] origin-left rounded-full bg-gradient-to-r from-slate-100/95 to-slate-300/5 shadow-[0_0_9px_rgba(210,230,255,0.45)]"
                      style={{ width: particle.length, maxWidth: 32 }}
                      animate={
                        reduceMotion
                          ? { opacity: 0.5, scaleX: 0.75 }
                          : { opacity: [0.08, 0.95, 0.12], scaleX: [0.3, 1, 0.55] }
                      }
                      transition={
                        reduceMotion
                          ? undefined
                          : {
                              repeat: Infinity,
                              duration: particle.duration,
                              delay: particle.delay,
                              ease: 'easeInOut',
                            }
                      }
                    />
                  </div>
                );
              })}

              <motion.div
                animate={
                  reduceMotion
                    ? { scale: 1, opacity: awakened ? 0.9 : 0.65 }
                    : {
                        scale: awakened ? [1, 1.09, 1] : [1, 1.035, 1],
                        opacity: awakened ? [0.72, 1, 0.72] : [0.55, 0.72, 0.55],
                      }
                }
                transition={reduceMotion ? undefined : { repeat: Infinity, duration: awakened ? 1.8 : 3.6, ease: 'easeInOut' }}
                className="absolute aspect-square w-[22%] rounded-full bg-[radial-gradient(circle,rgba(210,230,255,0.52)_0%,rgba(90,140,200,0.2)_35%,transparent_72%)] blur-[1px]"
              />

              <div className="relative z-10 text-center">
                <div className="mb-2 text-xl font-semibold tracking-[0.42em] text-white/95 md:text-3xl">
                  DRAGON
                </div>
                <div className="text-[10px] font-semibold tracking-[0.42em] text-slate-200/65 md:text-sm">
                  RESONANCE
                </div>
                <div className="mx-auto mt-5 h-px w-16 bg-gradient-to-r from-transparent via-slate-200/50 to-transparent" />
                <div className="mt-3 text-[9px] font-mono uppercase tracking-[0.24em] text-white/30">
                  Voice Soul · {mood}
                </div>
              </div>
            </div>

            <div className="z-10 w-full max-w-3xl flex-none rounded-2xl border border-white/10 bg-white/[0.035] p-4 backdrop-blur-xl md:p-5">
              <div className="mb-4 flex flex-wrap items-center justify-center gap-2">
                {moods.map((item) => (
                  <button
                    key={item}
                    type="button"
                    aria-pressed={mood === item}
                    onClick={() => setMood(item)}
                    className={`rounded-full border px-3 py-1.5 text-[9px] font-mono tracking-[0.12em] transition ${
                      mood === item
                        ? 'border-slate-200/45 bg-slate-100/10 text-white'
                        : 'border-white/10 bg-black/20 text-white/35 hover:text-white/65'
                    }`}
                  >
                    {item}
                  </button>
                ))}
              </div>

              <div className="grid gap-3 md:grid-cols-[1fr_auto] md:items-center">
                <div className="min-w-0">
                  <div className="mb-1 flex items-center gap-2 text-[9px] font-mono uppercase tracking-[0.18em] text-white/35">
                    <Volume2 className="h-3.5 w-3.5" />
                    Provider preview · Eleven v3 adapter
                  </div>
                  <p className="truncate text-xs text-slate-100/65 md:text-sm">{elevenPreview}</p>
                </div>

                <button
                  type="button"
                  onClick={awaken}
                  className="group flex items-center justify-center gap-2 rounded-xl border border-slate-100/30 bg-slate-100/[0.08] px-5 py-3 text-xs font-semibold tracking-[0.18em] text-white transition hover:bg-slate-100/[0.14]"
                >
                  {awakened ? <Sparkles className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
                  {awakened ? 'ACTIVE' : 'AWAKEN'}
                </button>
              </div>

              <div className="mt-3 flex items-center justify-between text-[8px] font-mono uppercase tracking-[0.15em] text-white/25">
                <span>Visual only · no hardware command sent</span>
                <span>schema {plan.schema}</span>
              </div>
            </div>
          </div>
        </motion.section>
      )}
    </AnimatePresence>
  );
};
