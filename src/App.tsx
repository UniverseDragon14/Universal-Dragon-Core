import React, { useEffect, useRef, useState } from 'react';
import { Analytics } from '@vercel/analytics/react';
import { Header } from './components/Header';
import { TelemetryPanel } from './components/TelemetryPanel';
import { SpatialMap } from './components/SpatialMap';
import { Terminal } from './components/Terminal';
import { ControlPanel } from './components/ControlPanel';
import { MatrixRain } from './components/MatrixRain';
import { ChatFeed } from './components/ChatFeed';
import { TelemetryData, MapPoint } from './types';
import { MOCK_LOG_MESSAGES } from './constants';

type ChatRole = 'user' | 'assistant';
type Mode = 'hacker' | 'builder' | 'research' | 'warroom' | 'oracle';

type ChatMessage = {
  id: string;
  role: ChatRole;
  text: string;
  createdAt: string;
};

const STORAGE_KEY = 'nova_secure_memory_final';
const MODE_KEY = 'nova_mode_final';

const generateCpuData = (length: number): TelemetryData[] =>
  Array.from({ length }, (_, i) => ({
    time: i,
    usage: Math.floor(Math.random() * 40) + 20,
    temp: Math.floor(Math.random() * 15) + 40,
  }));

const generateMapData = (): MapPoint[] =>
  Array.from({ length: 50 }, () => ({
    x: Math.random() * 200 - 100,
    y: Math.random() * 200 - 100,
    z: Math.random() * 100,
  }));

export default function App() {
  const [cpuData, setCpuData] = useState<TelemetryData[]>(generateCpuData(20));
  const [mapData, setMapData] = useState<MapPoint[]>(generateMapData());
  const [logs, setLogs] = useState<string[]>([]);
  const [message, setMessage] = useState('');
  const [liveReply, setLiveReply] = useState('');
  const [loading, setLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [autoSpeak, setAutoSpeak] = useState(false);
  const [systemState, setSystemState] = useState<'IDLE' | 'BREACHING'>('IDLE');

  const [mode, setMode] = useState<Mode>(() => {
    const saved = localStorage.getItem(MODE_KEY) as Mode | null;
    return saved || 'builder';
  });

  const [chatHistory, setChatHistory] = useState<ChatMessage[]>(() => {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return [
        {
          id: crypto.randomUUID(),
          role: 'assistant',
          text: 'NOVA CORE ONLINE.',
          createdAt: new Date().toISOString(),
        },
      ];
    }

    try {
      const parsed = JSON.parse(raw);
      return Array.isArray(parsed) && parsed.length
        ? parsed
        : [
            {
              id: crypto.randomUUID(),
              role: 'assistant',
              text: 'NOVA CORE ONLINE.',
              createdAt: new Date().toISOString(),
            },
          ];
    } catch {
      return [
        {
          id: crypto.randomUUID(),
          role: 'assistant',
          text: 'NOVA CORE ONLINE.',
          createdAt: new Date().toISOString(),
        },
      ];
    }
  });

  const chatContainerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(chatHistory));
  }, [chatHistory]);

  useEffect(() => {
    localStorage.setItem(MODE_KEY, mode);
  }, [mode]);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [chatHistory, liveReply, loading, isTyping]);

  useEffect(() => {
    const interval = setInterval(() => {
      setCpuData((prev) => {
        const lastTime = prev.length ? prev[prev.length - 1].time : 0;
        return [
          ...prev.slice(1),
          {
            time: lastTime + 1,
            usage: Math.floor(Math.random() * 40) + 20,
            temp: Math.floor(Math.random() * 15) + 40,
          },
        ];
      });

      setMapData(generateMapData());

      const timestamp = new Date().toISOString().split('T')[1].slice(0, -1);
      const randomMsg =
        MOCK_LOG_MESSAGES[Math.floor(Math.random() * MOCK_LOG_MESSAGES.length)];
      const newLog = `[SYS] ${timestamp} - ${randomMsg}`;
      setLogs((prev) => [...prev.slice(-12), newLog]);
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const playSound = (freq = 440, duration = 0.08) => {
    try {
      const AudioCtx =
        window.AudioContext ||
        (window as typeof window & { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;

      if (!AudioCtx) return;

      const ctx = new AudioCtx();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.frequency.setValueAtTime(freq, ctx.currentTime);
      gain.gain.setValueAtTime(0.01, ctx.currentTime);

      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.start();
      osc.stop(ctx.currentTime + duration);
    } catch {
      // ignore
    }
  };

  const speak = (text: string) => {
    if (!autoSpeak || !text.trim()) return;

    try {
      window.speechSynthesis.cancel();
      const speech = new SpeechSynthesisUtterance(text);
      speech.rate = 1.0;
      speech.pitch = 0.9;
      speech.lang = 'en-US';
      window.speechSynthesis.speak(speech);
    } catch {
      // ignore
    }
  };

  const clearMemory = () => {
    const reset: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'assistant',
      text: 'MEMORY CLEARED. FRESH CONTEXT INITIALIZED.',
      createdAt: new Date().toISOString(),
    };
    setChatHistory([reset]);
    setLiveReply('');
    localStorage.removeItem(STORAGE_KEY);
  };

  const exportMemory = () => {
    const blob = new Blob([JSON.stringify(chatHistory, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'nova-memory-final.json';
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleCommand = (input: string): string | null => {
    const cmd = input.trim().toLowerCase();

    if (!cmd.startsWith('/')) return null;

    if (cmd === '/help') {
      return [
        '# NOVA COMMANDS',
        '- /help',
        '- /clear',
        '- /export',
        '- /voice on',
        '- /voice off',
        '- /mode hacker',
        '- /mode builder',
        '- /mode research',
        '- /mode warroom',
        '- /mode oracle',
      ].join('\n');
    }

    if (cmd === '/clear') {
      clearMemory();
      return 'MEMORY CLEARED.';
    }

    if (cmd === '/export') {
      exportMemory();
      return 'MEMORY EXPORTED.';
    }

    if (cmd === '/voice on') {
      setAutoSpeak(true);
      return 'VOICE ENGINE ENABLED.';
    }

    if (cmd === '/voice off') {
      setAutoSpeak(false);
      window.speechSynthesis.cancel();
      return 'VOICE ENGINE DISABLED.';
    }

    if (cmd.startsWith('/mode ')) {
      const nextMode = cmd.replace('/mode ', '') as Mode;
      if (['hacker', 'builder', 'research', 'warroom', 'oracle'].includes(nextMode)) {
        setMode(nextMode);
        return `MODE SWITCHED TO ${nextMode.toUpperCase()}`;
      }
      return 'UNKNOWN MODE.';
    }

    return 'UNKNOWN COMMAND.';
  };

  const sendMessage = async () => {
    const trimmed = message.trim();
    if (!trimmed || loading) return;

    const commandReply = handleCommand(trimmed);
    if (commandReply) {
      const userMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'user',
        text: trimmed,
        createdAt: new Date().toISOString(),
      };

      const assistantMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        text: commandReply,
        createdAt: new Date().toISOString(),
      };

      setChatHistory((prev) => [...prev, userMsg, assistantMsg]);
      setMessage('');
      speak(commandReply);
      return;
    }

    setSystemState('BREACHING');
    playSound(880);

    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      text: trimmed,
      createdAt: new Date().toISOString(),
    };

    setChatHistory((prev) => [...prev, userMsg]);
    setMessage('');
    setLoading(true);
    setLiveReply('');

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: trimmed,
          history: chatHistory.slice(-8).map((m) => ({
            role: m.role,
            text: m.text,
          })),
          mode,
        }),
      });

      const data = await res.json();
      const aiReply = data?.reply || 'NO_RESPONSE';

      setIsTyping(true);

      let i = 0;
      let rendered = '';

      const animate = () => {
        if (i < aiReply.length) {
          rendered += aiReply.charAt(i);
          setLiveReply(rendered);
          i++;

          if (i % 4 === 0) playSound(1200, 0.03);
          setTimeout(animate, 10);
        } else {
          setIsTyping(false);
          setLoading(false);
          setSystemState('IDLE');

          const assistantMsg: ChatMessage = {
            id: crypto.randomUUID(),
            role: 'assistant',
            text: aiReply,
            createdAt: new Date().toISOString(),
          };

          setChatHistory((prev) => [...prev, assistantMsg]);
          setLiveReply('');
          speak(aiReply);
        }
      };

      animate();
    } catch {
      setLoading(false);
      setIsTyping(false);
      setSystemState('IDLE');

      const assistantMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        text: 'NEURAL_LINK_SEVERED.',
        createdAt: new Date().toISOString(),
      };

      setChatHistory((prev) => [...prev, assistantMsg]);
    }
  };

  return (
    <div
      className={`min-h-screen bg-black text-green-400 font-mono relative overflow-hidden ${
        systemState === 'BREACHING' ? 'scanline-active' : ''
      }`}
    >
      <MatrixRain />
      <div className="pointer-events-none fixed inset-0 z-50 opacity-[0.05] bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] bg-[size:100%_2px,3px_100%]" />

      <Header uptime="SYSTEM_ACTIVE" />

      <main className="relative z-10 grid grid-cols-12 gap-4 p-4 h-[calc(100vh-80px)]">
        <div className="hidden lg:flex lg:col-span-3 flex-col gap-4">
          <div className="border border-green-500/20 p-4 bg-black/60 backdrop-blur-md rounded-xl">
            <h3 className="text-[10px] text-green-700 uppercase mb-2 tracking-widest">
              Neural Load
            </h3>
            <TelemetryPanel data={cpuData} />
          </div>
          <Terminal logs={logs} />
        </div>

        <div className="col-span-12 lg:col-span-6 flex flex-col gap-4">
          <div className="flex-1 flex flex-col border-2 border-green-500/20 bg-black/80 rounded-2xl overflow-hidden shadow-2xl backdrop-blur-2xl">
            <div className="bg-green-500/10 p-3 flex justify-between border-b border-green-500/20">
              <span className="text-[10px] font-black uppercase tracking-widest">
                {systemState} // NOVA_FINAL
              </span>
              <span className="text-[9px] opacity-50">MODE: {mode.toUpperCase()}</span>
            </div>

            <ChatFeed
              chatHistory={chatHistory}
              liveReply={liveReply}
              loading={loading}
              isTyping={isTyping}
              chatContainerRef={chatContainerRef}
            />

            <div className="p-6 border-t border-green-500/20 bg-green-500/5">
              <input
                autoFocus
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
                placeholder="INJECT COMMAND..."
                className="w-full bg-transparent border-b border-green-500/30 pb-2 text-green-400 outline-none focus:border-green-500 font-mono"
              />

              <div className="mt-4 flex flex-wrap gap-2">
                <button
                  onClick={sendMessage}
                  className="px-6 py-2 bg-green-600 text-black font-black text-xs hover:bg-green-400"
                >
                  EXECUTE
                </button>

                <button
                  onClick={() => setAutoSpeak(!autoSpeak)}
                  className="px-4 py-2 border border-green-500/30 text-[10px]"
                >
                  {autoSpeak ? 'VOICE_ON' : 'VOICE_OFF'}
                </button>

                <button
                  onClick={() => setMode('hacker')}
                  className="px-4 py-2 border border-cyan-500/30 text-[10px]"
                >
                  HACKER
                </button>

                <button
                  onClick={() => setMode('builder')}
                  className="px-4 py-2 border border-cyan-500/30 text-[10px]"
                >
                  BUILDER
                </button>

                <button
                  onClick={() => setMode('oracle')}
                  className="px-4 py-2 border border-pink-500/30 text-[10px]"
                >
                  ORACLE
                </button>

                <button
                  onClick={clearMemory}
                  className="px-4 py-2 border border-red-500/30 text-[10px]"
                >
                  CLEAR
                </button>

                <button
                  onClick={exportMemory}
                  className="px-4 py-2 border border-yellow-500/30 text-[10px]"
                >
                  EXPORT
                </button>
              </div>
            </div>
          </div>
        </div>

        <div className="hidden lg:flex lg:col-span-3 flex-col gap-4">
          <SpatialMap data={mapData} />
          <ControlPanel />
        </div>
      </main>

      <style>{`
        .scanline-active::after {
          content: "";
          position: fixed;
          inset: 0;
          pointer-events: none;
          z-index: 100;
          background:
            linear-gradient(rgba(18,16,16,0) 50%, rgba(0,0,0,0.25) 50%),
            linear-gradient(90deg, rgba(255,0,0,0.06), rgba(0,255,0,0.02), rgba(0,0,255,0.06));
          background-size: 100% 2px, 3px 100%;
        }

        .scrollbar-hide::-webkit-scrollbar {
          display: none;
        }
      `}</style>
      <Analytics />
    </div>
  );
}
