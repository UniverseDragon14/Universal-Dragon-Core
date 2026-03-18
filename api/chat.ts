import React, { useEffect, useRef, useState, useMemo, useCallback } from 'react';
import { Header } from './components/Header';
import { SpatialMap } from './components/SpatialMap';
import { Terminal } from './components/Terminal';
import { ControlPanel } from './components/ControlPanel';

type ChatRole = 'user' | 'assistant';
type ChatMessage = {
  id: number;
  role: ChatRole;
  text: string;
};

type PayloadFile = {
  data: string;
  type: string;
};

type MemoryItem = {
  id: number;
  query: string;
  response: string;
};

const MEMORY_KEY = 'nova_neural_brain';
const MAX_MEMORY = 20;
const MAX_HISTORY_SEND = 5;

// ==========================================
// 🧠 SAFE NEURAL MEMORY CORE
// ==========================================
function useNeuralMemory() {
  const [memory, setMemory] = useState<MemoryItem[]>([]);

  useEffect(() => {
    try {
      const raw = localStorage.getItem(MEMORY_KEY);
      if (!raw) return;
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed)) {
        setMemory(parsed.slice(-MAX_MEMORY));
      }
    } catch {
      setMemory([]);
    }
  }, []);

  const persist = (updated: MemoryItem[]) => {
    setMemory(updated);
    try {
      localStorage.setItem(MEMORY_KEY, JSON.stringify(updated));
    } catch {}
  };

  const injectMemory = useCallback((userMessage: string, aiResponse: string) => {
    if (!userMessage || userMessage.trim().length < 10) return;

    const newMem: MemoryItem = {
      id: Date.now(),
      query: userMessage.trim(),
      response: aiResponse.slice(0, 200),
    };

    const updated = [...memory, newMem].slice(-MAX_MEMORY);
    persist(updated);
  }, [memory]);

  const recallMemory = useCallback((query: string) => {
    const words = query
      .toLowerCase()
      .split(/\s+/)
      .map(w => w.trim())
      .filter(w => w.length > 4);

    if (!words.length || !memory.length) return 'NO_PAST_DATA';

    const matches = memory.filter(item =>
      words.some(word => item.query.toLowerCase().includes(word))
    );

    if (!matches.length) return 'NO_PAST_DATA';

    return matches
      .slice(-3)
      .map(item => `Past context: ${item.response}`)
      .join(' | ');
  }, [memory]);

  return { injectMemory, recallMemory };
}

// ==========================================
// 💻 SAFE-ish MARKDOWN VIEW
// ==========================================
function MarkdownView({
  text,
  onRunCode,
}: {
  text: string;
  onRunCode: (code: string) => void;
}) {
  const blocks = text.split('```');

  return (
    <div className="space-y-4 font-mono text-sm leading-relaxed">
      {blocks.map((block, index) => {
        const isCode = index % 2 === 1;

        if (isCode) {
          const codeLines = block.split('\n');
          const lang = codeLines.shift()?.trim().toLowerCase() || '';
          const pureCode = codeLines.join('\n');

          return (
            <div
              key={index}
              className="relative rounded-xl border border-white/20 bg-black/80 shadow-2xl overflow-hidden group"
            >
              <div className="bg-white/10 px-4 py-1 text-[10px] uppercase text-cyan-400 font-bold flex justify-between items-center">
                <span>{lang || 'code'}</span>

                {(lang.includes('js') || lang.includes('javascript')) && (
                  <button
                    onClick={() => onRunCode(pureCode)}
                    className="bg-cyan-500 text-black px-3 py-1 rounded hover:bg-white transition-all shadow-[0_0_10px_#00ffff]"
                  >
                    [ RUN CODE ]
                  </button>
                )}
              </div>
              <pre className="p-4 text-xs text-green-300 overflow-x-auto">
                <code>{pureCode}</code>
              </pre>
            </div>
          );
        }

        return block
          .split('\n')
          .filter(line => line.trim() !== '')
          .map((line, li) => {
            if (line.startsWith('# ')) {
              return (
                <h1
                  key={`${index}-${li}`}
                  className="text-xl font-black text-white uppercase tracking-tighter mb-2"
                >
                  / {line.replace('# ', '')}
                </h1>
              );
            }

            if (line.startsWith('- ')) {
              return (
                <div key={`${index}-${li}`} className="pl-4 opacity-80 text-white/90">
                  • {line.replace('- ', '')}
                </div>
              );
            }

            return (
              <p key={`${index}-${li}`} className="opacity-90 text-white/90">
                {line}
              </p>
            );
          });
      })}
    </div>
  );
}

// ==========================================
// 🌌 MATRIX RAIN
// ==========================================
function MatrixRain({ color }: { color: string }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    resize();
    window.addEventListener('resize', resize);

    const chars = '01🐉7DNOVA⚡ASLAM01';
    let drops = new Array(Math.floor(canvas.width / 14)).fill(1);

    const draw = () => {
      ctx.fillStyle = 'rgba(0,0,0,0.1)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      ctx.fillStyle = color;
      ctx.shadowBlur = 5;
      ctx.shadowColor = color;
      ctx.font = 'bold 14px monospace';

      drops.forEach((y, i) => {
        ctx.fillText(chars[Math.floor(Math.random() * chars.length)], i * 14, y * 14);

        if (y * 14 > canvas.height && Math.random() > 0.975) drops[i] = 0;
        drops[i]++;
      });
    };

    const interval = window.setInterval(draw, 33);

    return () => {
      window.clearInterval(interval);
      window.removeEventListener('resize', resize);
    };
  }, [color]);

  return <canvas ref={canvasRef} className="fixed inset-0 opacity-20 pointer-events-none z-0" />;
}

// ==========================================
// 👑 MAIN APP
// ==========================================
export default function App() {
  const [message, setMessage] = useState('');
  const [liveReply, setLiveReply] = useState('');
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState('hacker');
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [payload, setPayload] = useState<PayloadFile | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [autoSpeak, setAutoSpeak] = useState(false);

  const chatRef = useRef<HTMLDivElement>(null);
  const { injectMemory, recallMemory } = useNeuralMemory();

  const modeColor = useMemo(
    () =>
      (
        {
          hacker: '#00ff66',
          oracle: '#ff00ff',
          warroom: '#ff3131',
          builder: '#00f2ff',
        } as Record<string, string>
      )[mode] || '#00ff66',
    [mode]
  );

  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [chatHistory, liveReply]);

  const addLog = useCallback((line: string) => {
    setLogs(prev => [...prev.slice(-10), line]);
  }, []);

  const speak = useCallback((text: string) => {
    if (!autoSpeak || typeof window === 'undefined' || !('speechSynthesis' in window)) return;

    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text.replace(/[*#`_]/g, ''));
    utterance.rate = 1.05;
    utterance.pitch = 0.85;

    window.speechSynthesis.speak(utterance);
  }, [autoSpeak]);

  const playSound = useCallback((f = 800) => {
    try {
      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
      if (!AudioCtx) return;

      const ctx = new AudioCtx();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.frequency.value = f;
      gain.gain.value = 0.01;

      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.start();
      osc.stop(ctx.currentTime + 0.1);

      setTimeout(() => {
        try {
          ctx.close();
        } catch {}
      }, 150);
    } catch {}
  }, []);

  const handleFileUpload = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();

    reader.onloadend = () => {
      const result = reader.result;
      if (typeof result !== 'string') return;

      const base64 = result.split(',')[1];
      if (!base64) return;

      setPayload({
        data: base64,
        type: file.type,
      });

      playSound(1200);
      addLog(`[UPLOAD] Payload attached: ${file.name}`);
    };

    reader.readAsDataURL(file);
  }, [addLog, playSound]);

  // WARNING: still not truly secure. Better disable eval in production.
  const runNeuralCode = useCallback((code: string) => {
    playSound(2000);
    addLog('[SANDBOX] Executing neural script...');

    try {
      if (
        code.includes('fetch(') ||
        code.includes('localStorage') ||
        code.includes('sessionStorage') ||
        code.includes('document.') ||
        code.includes('window.location') ||
        code.includes('eval(') ||
        code.includes('Function(')
      ) {
        throw new Error('Blocked unsafe operation in sandbox');
      }

      const output: string[] = [];
      const safeConsole = {
        log: (...args: unknown[]) => output.push(args.map(String).join(' ')),
      };

      const fn = new Function('console', `"use strict";\n${code}`);
      fn(safeConsole);

      addLog(`[OUTPUT]: ${output.join(' | ') || 'Success (No console output)'}`);
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Unknown sandbox error';
      addLog(`[ERROR]: ${msg}`);
    }
  }, [addLog, playSound]);

  const sendMessage = useCallback(async () => {
    if (!message.trim() || loading) return;

    const currentMessage = message.trim();
    setLoading(true);
    playSound(900);

    const pastMemory = recallMemory(currentMessage);
    const hiddenPrompt = `[INTERNAL MEMORY: ${pastMemory}] USER_SAYS: ${currentMessage}`;

    const userMsg: ChatMessage = {
      role: 'user',
      text: currentMessage,
      id: Date.now(),
    };

    const nextHistory = [...chatHistory, userMsg];
    setChatHistory(nextHistory);
    setMessage('');
    setLiveReply('');

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: hiddenPrompt,
          history: nextHistory.slice(-MAX_HISTORY_SEND),
          mode,
          image: payload?.type.startsWith('image') ? payload : null,
          audio: payload?.type.startsWith('audio') ? payload : null,
        }),
      });

      if (!res.ok) {
        const errorText = await res.text().catch(() => 'API request failed');
        throw new Error(errorText || 'API request failed');
      }

      if (!res.body) {
        throw new Error('Response body missing');
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let fullText = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        fullText += decoder.decode(value, { stream: true });
        setLiveReply(fullText);

        if (fullText.length > 0 && fullText.length % 60 === 0) {
          playSound(1500);
        }
      }

      setChatHistory(prev => [
        ...prev,
        {
          role: 'assistant',
          text: fullText || 'NO_RESPONSE_FROM_CORE',
          id: Date.now() + 1,
        },
      ]);

      injectMemory(currentMessage, fullText);
      speak(fullText);
      setLiveReply('');
      setPayload(null);
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'CRITICAL_ERROR: OMNI_LINK_SEVERED';
      setLiveReply('');
      setChatHistory(prev => [
        ...prev,
        {
          role: 'assistant',
          text: `CRITICAL_ERROR: ${msg}`,
          id: Date.now() + 1,
        },
      ]);
      addLog(`[API ERROR] ${msg}`);
    } finally {
      setLoading(false);
    }
  }, [
    message,
    loading,
    recallMemory,
    chatHistory,
    mode,
    payload,
    playSound,
    injectMemory,
    speak,
    addLog,
  ]);

  return (
    <div
      className="min-h-screen bg-black transition-all duration-1000 overflow-hidden font-mono select-none"
      style={{ color: modeColor }}
    >
      <MatrixRain color={modeColor} />
      <div className="fixed inset-0 z-50 pointer-events-none opacity-5 bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] bg-[size:100%_2px,3px_100%]" />

      <Header uptime="OMNIPOTENT_MODE" />

      <main className="relative z-10 grid grid-cols-12 gap-4 p-4 h-[calc(100vh-80px)]">
        <div className="hidden lg:flex lg:col-span-3 flex-col gap-4">
          <div className="border border-white/10 p-4 bg-black/80 rounded-2xl backdrop-blur-xl shadow-2xl">
            <h3 className="text-[10px] opacity-50 uppercase tracking-[0.2em] mb-3">
              System Override
            </h3>
            <button
              onClick={() => setAutoSpeak(!autoSpeak)}
              className={`w-full py-2 border rounded-lg text-xs font-bold transition-all ${
                autoSpeak
                  ? 'bg-cyan-500 text-black shadow-[0_0_15px_#00ffff]'
                  : 'border-white/20 hover:bg-white/10'
              }`}
            >
              🎙️ {autoSpeak ? 'JARVIS VOICE: ON' : 'JARVIS VOICE: OFF'}
            </button>
          </div>
          <Terminal logs={logs} />
        </div>

        <div className="col-span-12 lg:col-span-6 flex flex-col border-2 border-white/10 bg-black/85 rounded-3xl overflow-hidden backdrop-blur-3xl shadow-[0_0_60px_rgba(0,0,0,0.8)]">
          <div className="p-4 border-b border-white/10 flex justify-between items-center bg-white/5">
            <span className="text-xs font-black tracking-widest animate-pulse">
              NOVA_v15_OMNI // {mode.toUpperCase()}
            </span>

            <div className="flex gap-2">
              {['hacker', 'builder', 'warroom', 'oracle'].map(m => (
                <button
                  key={m}
                  onClick={() => {
                    setMode(m);
                    playSound(400);
                  }}
                  className={`px-3 py-1 text-[9px] border border-white/10 rounded-full ${
                    mode === m ? 'bg-white/20 scale-105' : 'opacity-30'
                  }`}
                >
                  {m.toUpperCase()}
                </button>
              ))}
            </div>
          </div>

          <div ref={chatRef} className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-hide">
            {chatHistory.map(m => (
              <div key={m.id} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div
                  className="max-w-[90%] p-5 rounded-3xl border bg-white/5 backdrop-blur-md"
                  style={{ borderColor: `${modeColor}40` }}
                >
                  <div className="text-[9px] opacity-40 mb-2 uppercase tracking-widest">
                    {m.role === 'user' ? 'CREATOR ASLAM' : 'NOVA OMNI-CORE'}
                  </div>
                  <MarkdownView text={m.text} onRunCode={runNeuralCode} />
                </div>
              </div>
            ))}

            {liveReply && (
              <div className="max-w-[90%] p-5 border border-white/10 bg-white/5 rounded-3xl animate-pulse">
                <MarkdownView text={liveReply} onRunCode={() => {}} />
                <div className="w-1.5 h-4 ml-1 inline-block animate-ping bg-current align-middle" />
              </div>
            )}
          </div>

          <div className="p-6 border-t border-white/10 bg-white/5 flex items-center gap-4">
            <input type="file" id="up" className="hidden" onChange={handleFileUpload} />
            <label
              htmlFor="up"
              className={`cursor-pointer text-2xl ${
                payload ? 'text-pink-500 animate-pulse' : 'opacity-40 hover:opacity-100'
              }`}
            >
              📎
            </label>

            <input
              autoFocus
              value={message}
              onChange={e => setMessage(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && sendMessage()}
              placeholder={payload ? 'Payload encoded. Command?' : 'Access Omni-Matrix...'}
              className="flex-1 bg-transparent border-b border-white/20 pb-2 outline-none focus:border-white/50 text-lg"
            />

            <button
              onClick={sendMessage}
              disabled={loading}
              className="px-8 py-3 font-black text-xs hover:brightness-125 active:scale-95 rounded-xl shadow-lg disabled:opacity-50"
              style={{ backgroundColor: modeColor, color: '#000' }}
            >
              {loading ? 'LINKING...' : 'EXECUTE'}
            </button>
          </div>
        </div>

        <div className="hidden lg:flex lg:col-span-3 flex-col gap-4">
          <SpatialMap />
          <ControlPanel />
        </div>
      </main>

      <style>{`.scrollbar-hide::-webkit-scrollbar { display: none; }`}</style>
    </div>
  );
}
