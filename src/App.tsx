import React, { useEffect, useRef, useState, useMemo } from 'react';
// மற்ற காம்போனென்ட்கள் (Header, Telemetry போன்றவை) ஏற்கனவே இருப்பவை என்பதால் அவற்றை அப்படியே இம்போர்ட் செய்கிறோம்
import { Header } from './components/Header';
import { TelemetryPanel } from './components/TelemetryPanel';
import { SpatialMap } from './components/SpatialMap';
import { Terminal } from './components/Terminal';
import { ControlPanel } from './components/ControlPanel';
import { TelemetryData, MapPoint } from './types';
import { MOCK_LOG_MESSAGES } from './constants';

// ==========================================
// 1. TYPES & CONSTANTS
// ==========================================
type ChatRole = 'user' | 'assistant';
type Mode = 'hacker' | 'builder' | 'research' | 'warroom';
type ChatMessage = { id: string; role: ChatRole; text: string; createdAt: string; };

const STORAGE_KEY = 'nova_secure_memory_v6';
const MODE_KEY = 'nova_mode_v6';

// ==========================================
// 2. INTERNAL COMPONENTS (MatrixRain & Markdown)
// ==========================================
function MatrixRain() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  useEffect(() => {
    const canvas = canvasRef.current; if (!canvas) return;
    const ctx = canvas.getContext('2d'); if (!ctx) return;
    const resize = () => { canvas.width = window.innerWidth; canvas.height = window.innerHeight; };
    resize(); window.addEventListener('resize', resize);
    const chars = '01010101ABCDEFあいうえお';
    const fontSize = 14;
    let drops = new Array(Math.floor(canvas.width / fontSize)).fill(1);
    const draw = () => {
      ctx.fillStyle = 'rgba(0, 0, 0, 0.06)'; ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = '#00ff66'; ctx.font = `${fontSize}px monospace`;
      for (let i = 0; i < drops.length; i++) {
        const text = chars.charAt(Math.floor(Math.random() * chars.length));
        ctx.fillText(text, i * fontSize, drops[i] * fontSize);
        if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) drops[i] = 0;
        drops[i]++;
      }
    };
    const interval = setInterval(draw, 33);
    return () => { clearInterval(interval); window.removeEventListener('resize', resize); };
  }, []);
  return <canvas ref={canvasRef} className="fixed inset-0 opacity-10 pointer-events-none" />;
}

function MarkdownView({ text }: { text: string }) {
  const blocks = text.split('```');
  return (
    <div className="space-y-3">
      {blocks.map((block, index) => {
        const isCode = index % 2 === 1;
        if (isCode) return <pre key={index} className="overflow-x-auto rounded-lg border border-cyan-500/20 bg-black/60 p-3 text-xs text-cyan-200"><code>{block.trim()}</code></pre>;
        return block.split('\n').filter(l => l.trim() !== '').map((line, li) => (
          <p key={`${index}-${li}`} className="whitespace-pre-wrap leading-relaxed">{line}</p>
        ));
      })}
    </div>
  );
}

// ==========================================
// 3. MAIN APP CORE
// ==========================================
export default function App() {
  // --- States ---
  const [message, setMessage] = useState('');
  const [liveReply, setLiveReply] = useState('');
  const [loading, setLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [systemState, setSystemState] = useState<'IDLE' | 'BREACHING'>('IDLE');
  const [autoSpeak, setAutoSpeak] = useState(false);
  const [micListening, setMicListening] = useState(false);
  const [mode, setMode] = useState<Mode>((localStorage.getItem(MODE_KEY) as Mode) || 'builder');
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>(() => {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [{ id: '1', role: 'assistant', text: 'NOVA CORE ONLINE.', createdAt: new Date().toISOString() }];
  });
  
  // --- Telemetry States (Simplified for space) ---
  const [cpuData, setCpuData] = useState<TelemetryData[]>(Array.from({ length: 20 }, (_, i) => ({ time: i, usage: 30, temp: 45 })));
  const [mapData, setMapData] = useState<MapPoint[]>([]);
  const [logs, setLogs] = useState<string[]>([]);
  const chatContainerRef = useRef<HTMLDivElement | null>(null);

  // --- Effects ---
  useEffect(() => localStorage.setItem(STORAGE_KEY, JSON.stringify(chatHistory)), [chatHistory]);
  useEffect(() => localStorage.setItem(MODE_KEY, mode), [mode]);
  useEffect(() => { if (chatContainerRef.current) chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight; }, [chatHistory, liveReply]);

  // --- Voice Engine ---
  const speak = (text: string) => {
    if (!autoSpeak) return;
    window.speechSynthesis.cancel();
    const speech = new SpeechSynthesisUtterance(text);
    speech.rate = 1.0; speech.pitch = 0.9;
    window.speechSynthesis.speak(speech);
  };

  // --- Audio Feedback ---
  const playSound = (freq = 440) => {
    const ctx = new (window.AudioContext || (window as any).webkitAudioContext)();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.frequency.setValueAtTime(freq, ctx.currentTime);
    gain.gain.setValueAtTime(0.01, ctx.currentTime);
    osc.connect(gain); gain.connect(ctx.destination);
    osc.start(); osc.stop(ctx.currentTime + 0.1);
  };

  // --- Send Message Logic ---
  const sendMessage = async () => {
    if (!message.trim() || loading) return;
    setSystemState('BREACHING'); playSound(880);
    const userMsg = { id: crypto.randomUUID(), role: 'user' as const, text: message, createdAt: new Date().toISOString() };
    setChatHistory(prev => [...prev, userMsg]);
    setLoading(true); setMessage('');

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg.text, history: chatHistory.slice(-5), mode }),
      });
      const data = await res.json();
      const aiReply = data.reply || "ERROR: NO_RESPONSE";

      setIsTyping(true);
      let i = 0; let rendered = '';
      const fastType = () => {
        if (i < aiReply.length) {
          rendered += aiReply.charAt(i); setLiveReply(rendered); i++;
          if (i % 4 === 0) playSound(1200);
          setTimeout(fastType, 10);
        } else {
          setIsTyping(false); setSystemState('IDLE');
          setChatHistory(prev => [...prev, { id: crypto.randomUUID(), role: 'assistant', text: aiReply, createdAt: new Date().toISOString() }]);
          setLiveReply(''); speak(aiReply);
        }
      };
      fastType();
    } catch {
      setSystemState('IDLE'); setLoading(false);
    }
  };

  return (
    <div className={`min-h-screen bg-black text-green-400 font-mono relative overflow-hidden ${systemState === 'BREACHING' ? 'scanline-active' : ''}`}>
      <MatrixRain />
      <div className="pointer-events-none fixed inset-0 z-50 opacity-[0.05] bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] bg-[size:100%_2px,3px_100%]" />
      
      <Header uptime="SYSTEM_ACTIVE" />

      <main className="relative z-10 grid grid-cols-12 gap-4 p-4 h-[calc(100vh-80px)]">
        {/* LEFT PANEL */}
        <div className="hidden lg:flex lg:col-span-3 flex-col gap-4">
          <div className="border border-green-500/20 p-4 bg-black/60 backdrop-blur-md">
            <h3 className="text-[10px] text-green-700 uppercase mb-2 tracking-widest">Neural Load</h3>
            <TelemetryPanel data={cpuData} />
          </div>
          <Terminal logs={logs} />
        </div>

        {/* CENTER PANEL */}
        <div className="col-span-12 lg:col-span-6 flex flex-col gap-4">
          <div className="flex-1 flex flex-col border-2 border-green-500/20 bg-black/80 rounded-2xl overflow-hidden shadow-2xl backdrop-blur-2xl">
            <div className="bg-green-500/10 p-3 flex justify-between border-b border-green-500/20">
              <span className="text-[10px] font-black uppercase tracking-widest">{systemState} // NOVA_v6.0</span>
              <span className="text-[9px] opacity-50">MODE: {mode.toUpperCase()}</span>
            </div>

            <div className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-hide" ref={chatContainerRef}>
              {chatHistory.map((item) => (
                <div key={item.id} className={`flex ${item.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[85%] p-4 border ${item.role === 'user' ? 'border-green-500/40 bg-green-500/5' : 'border-blue-500/30 bg-blue-500/5 text-blue-100'} rounded-2xl`}>
                    <div className="text-[8px] opacity-50 mb-1 tracking-tighter">{item.role.toUpperCase()}</div>
                    <MarkdownView text={item.text} />
                  </div>
                </div>
              ))}
              {(liveReply || loading) && (
                <div className="flex justify-start"><div className="max-w-[85%] p-4 border border-pink-500/40 bg-pink-500/5 text-pink-100 rounded-2xl">
                  <MarkdownView text={liveReply || 'Analyzing...'} />
                </div></div>
              )}
            </div>

            <div className="p-6 border-t border-green-500/20 bg-green-500/5">
              <input
                autoFocus value={message} onChange={e => setMessage(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && sendMessage()}
                placeholder="INJECT COMMAND..."
                className="w-full bg-transparent border-b border-green-500/30 pb-2 text-green-400 outline-none focus:border-green-500 font-mono"
              />
              <div className="mt-4 flex gap-2">
                <button onClick={sendMessage} className="px-6 py-2 bg-green-600 text-black font-black text-xs hover:bg-green-400">EXECUTE</button>
                <button onClick={() => setAutoSpeak(!autoSpeak)} className="px-4 py-2 border border-green-500/30 text-[10px]">{autoSpeak ? 'VOICE_ON' : 'VOICE_OFF'}</button>
              </div>
            </div>
          </div>
        </div>

        {/* RIGHT PANEL */}
        <div className="hidden lg:flex lg:col-span-3 flex-col gap-4">
          <SpatialMap data={mapData} />
          <ControlPanel />
        </div>
      </main>

      <style>{`
        .scanline-active::after { content: ""; position: fixed; inset: 0; pointer-events: none; z-index: 100; background: linear-gradient(rgba(18,16,16,0) 50%, rgba(0,0,0,0.25) 50%), linear-gradient(90deg, rgba(255,0,0,0.06), rgba(0,255,0,0.02), rgba(0,0,255,0.06)); background-size: 100% 2px, 3px 100%; }
        .scrollbar-hide::-webkit-scrollbar { display: none; }
      `}</style>
    </div>
  );
}
