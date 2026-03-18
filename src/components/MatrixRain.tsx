import React, { useEffect, useRef, useState, useMemo } from 'react';
// எக்ஸ்டர்னல் காம்போனென்ட்ஸ் (உங்க ப்ராஜெக்ட்ல ஏற்கனவே இருப்பவை)
import { Header } from './components/Header';
import { TelemetryPanel } from './components/TelemetryPanel';
import { SpatialMap } from './components/SpatialMap';
import { Terminal } from './components/Terminal';
import { ControlPanel } from './components/ControlPanel';
import { TelemetryData, MapPoint } from './types';
import { MOCK_LOG_MESSAGES } from './constants';

// ==========================================
// 1. TYPES & SECURE KEYS
// ==========================================
type ChatRole = 'user' | 'assistant';
type Mode = 'hacker' | 'builder' | 'research' | 'warroom' | 'oracle';
type ChatMessage = { id: string; role: ChatRole; text: string; createdAt: string; image?: boolean; };

const STORAGE_KEY = 'nova_ultimate_memory_v10';
const MODE_KEY = 'nova_mode_v10';

// ==========================================
// 2. INTERNAL COMPONENT: NEURAL MARKDOWN
// ==========================================
function MarkdownView({ text }: { text: string }) {
  const blocks = text.split('```');
  return (
    <div className="space-y-3 font-mono text-sm leading-relaxed">
      {blocks.map((block, index) => {
        const isCode = index % 2 === 1;
        if (isCode) return (
          <pre key={index} className="overflow-x-auto rounded-lg border border-white/10 bg-black/60 p-3 text-xs text-cyan-300 shadow-inner">
            <code>{block.trim()}</code>
          </pre>
        );
        return block.split('\n').filter(l => l.trim() !== '').map((line, li) => {
          if (line.startsWith('# ')) return <h1 key={li} className="text-lg font-black border-b border-white/10 pb-1 mb-2">/ {line.replace('# ', '')}</h1>;
          if (line.startsWith('- ')) return <div key={li} className="pl-4 opacity-80">• {line.replace('- ', '')}</div>;
          return <p key={li} className="opacity-90">{line}</p>;
        });
      })}
    </div>
  );
}

// ==========================================
// 3. INTERNAL COMPONENT: DRAGON MATRIX RAIN
// ==========================================
function MatrixRain({ color = '#0f0' }: { color?: string }) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  useEffect(() => {
    const canvas = canvasRef.current; if (!canvas) return;
    const ctx = canvas.getContext('2d'); if (!ctx) return;
    const resize = () => { canvas.width = window.innerWidth; canvas.height = window.innerHeight; };
    resize(); window.addEventListener('resize', resize);
    const chars = "01🐉NOVA⚡ASLAM01"; const fontSize = 14;
    let drops = new Array(Math.floor(canvas.width / fontSize)).fill(1);
    const draw = () => {
      ctx.fillStyle = 'rgba(0, 0, 0, 0.08)'; ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.shadowBlur = 5; ctx.shadowColor = color;
      ctx.fillStyle = color; ctx.font = `${fontSize}px monospace`;
      drops.forEach((y, i) => {
        const text = chars[Math.floor(Math.random() * chars.length)];
        ctx.fillText(text, i * fontSize, y * fontSize);
        if (y * fontSize > canvas.height && Math.random() > 0.975) drops[i] = 0;
        drops[i]++;
      });
    };
    const interval = setInterval(draw, 33);
    return () => { clearInterval(interval); window.removeEventListener('resize', resize); };
  }, [color]);
  return <canvas ref={canvasRef} className="fixed inset-0 opacity-15 pointer-events-none z-0" />;
}

// ==========================================
// 4. MAIN APP CORE: DRAGON NOVA ULTIMATE
// ==========================================
export default function App() {
  const [message, setMessage] = useState('');
  const [liveReply, setLiveReply] = useState('');
  const [loading, setLoading] = useState(false);
  const [systemState, setSystemState] = useState<'IDLE' | 'BREACHING'>('IDLE');
  const [mode, setMode] = useState<Mode>((localStorage.getItem(MODE_KEY) as Mode) || 'builder');
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>(() => {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [{ id: '1', role: 'assistant', text: 'NOVA CORE ONLINE. AWAITING CREATOR ASLAM.', createdAt: new Date().toISOString() }];
  });
  const [image, setImage] = useState<{data: string, mime_type: string} | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  
  const chatContainerRef = useRef<HTMLDivElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // --- Dynamic UI Colors ---
  const modeColor = useMemo(() => {
    const map = { hacker: '#00ff66', builder: '#00f2ff', warroom: '#ff3131', oracle: '#ff00ff', research: '#3182ce' };
    return map[mode] || '#00ff66';
  }, [mode]);

  // --- Telemetry Animation ---
  const [cpuData, setCpuData] = useState<TelemetryData[]>(Array.from({ length: 20 }, (_, i) => ({ time: i, usage: 30, temp: 45 })));
  useEffect(() => {
    const interval = setInterval(() => {
      setCpuData(prev => [...prev.slice(1), { time: prev[prev.length-1].time + 1, usage: Math.floor(Math.random()*40)+20, temp: 45 }]);
      const timestamp = new Date().toLocaleTimeString();
      setLogs(prev => [...prev.slice(-10), `[SYS] ${timestamp} - ${MOCK_LOG_MESSAGES[Math.floor(Math.random()*MOCK_LOG_MESSAGES.length)]}`]);
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => { localStorage.setItem(STORAGE_KEY, JSON.stringify(chatHistory)); localStorage.setItem(MODE_KEY, mode); }, [chatHistory, mode]);
  useEffect(() => { if (chatContainerRef.current) chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight; }, [chatHistory, liveReply]);

  const playSound = (freq = 440) => {
    try {
      const ctx = new (window.AudioContext || (window as any).webkitAudioContext)();
      const osc = ctx.createOscillator(); const gain = ctx.createGain();
      osc.frequency.setValueAtTime(freq, ctx.currentTime); gain.gain.setValueAtTime(0.01, ctx.currentTime);
      osc.connect(gain); gain.connect(ctx.destination); osc.start(); osc.stop(ctx.currentTime + 0.1);
    } catch {}
  };

  const handleImage = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => { setImage({ data: (reader.result as string).split(',')[1], mime_type: file.type }); playSound(600); };
      reader.readAsDataURL(file);
    }
  };

  const sendMessage = async () => {
    if (!message.trim() || loading) return;
    setLoading(true); setSystemState('BREACHING'); playSound(800);
    const userMsg = { id: crypto.randomUUID(), role: 'user' as const, text: message, createdAt: new Date().toISOString(), image: !!image };
    setChatHistory(prev => [...prev, userMsg]); setMessage('');

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg.text, history: chatHistory.slice(-5), mode, image }),
      });

      if (!res.body) throw new Error();
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let fullText = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        fullText += decoder.decode(value);
        setLiveReply(fullText);
        if (fullText.length % 15 === 0) playSound(1200);
      }

      setChatHistory(prev => [...prev, { id: crypto.randomUUID(), role: 'assistant', text: fullText, createdAt: new Date().toISOString() }]);
      setLiveReply(''); setImage(null);
    } catch {
      setChatHistory(prev => [...prev, { id: crypto.randomUUID(), role: 'assistant', text: "NEURAL_LINK_SEVERED", createdAt: new Date().toISOString() }]);
    } finally {
      setLoading(false); setSystemState('IDLE');
    }
  };

  return (
    <div className="min-h-screen bg-black font-mono transition-colors duration-1000" style={{ color: modeColor }}>
      <MatrixRain color={modeColor} />
      <div className="pointer-events-none fixed inset-0 z-50 opacity-[0.05] bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] bg-[size:100%_2px,3px_100%]" />
      
      <Header uptime="NOVA_GOD_MODE_ACTIVE" />

      <main className="relative z-10 grid grid-cols-12 gap-4 p-4 h-[calc(100vh-80px)]">
        <div className="hidden lg:flex lg:col-span-3 flex-col gap-4">
          <div className="border border-white/10 p-4 bg-black/60 rounded-xl backdrop-blur-md shadow-2xl">
            <h3 className="text-[10px] opacity-50 uppercase tracking-widest mb-2">Neural Telemetry</h3>
            <TelemetryPanel data={cpuData} />
          </div>
          <Terminal logs={logs} />
        </div>

        <div className="col-span-12 lg:col-span-6 flex flex-col gap-4">
          <div className="flex-1 flex flex-col border-2 border-white/10 bg-black/80 rounded-3xl overflow-hidden shadow-[0_0_50px_rgba(0,0,0,0.5)] backdrop-blur-3xl">
            <div className="bg-white/5 p-4 flex justify-between items-center border-b border-white/10">
              <span className="text-xs font-black tracking-widest uppercase animate-pulse">{systemState} // NOVA_ULTIMATE_v10</span>
              <div className="flex gap-2">
                {['hacker', 'builder', 'warroom', 'oracle'].map(m => (
                  <button key={m} onClick={() => setMode(m as any)} className={`px-2 py-1 text-[9px] border border-white/10 ${mode === m ? 'bg-white/20' : 'opacity-40'}`}>{m.toUpperCase()}</button>
                ))}
              </div>
            </div>

            <div ref={chatContainerRef} className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-hide">
              {chatHistory.map((item) => (
                <div key={item.id} className={`flex ${item.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className="max-w-[85%] p-4 rounded-2xl border bg-white/5 backdrop-blur-sm shadow-xl" style={{ borderColor: `${modeColor}40` }}>
                    <div className="text-[9px] opacity-30 mb-2 uppercase tracking-tighter">{item.role === 'user' ? '>> CREATOR' : '>> NOVA'} {item.image && '[VISUAL]'}</div>
                    <MarkdownView text={item.text} />
                  </div>
                </div>
              ))}
              {(liveReply || loading) && (
                <div className="flex justify-start">
                  <div className="max-w-[85%] p-4 border border-white/10 bg-white/5 rounded-2xl animate-in fade-in">
                    <MarkdownView text={liveReply || 'Accessing neural pathways...'} />
                    <div className="w-1 h-4 ml-1 inline-block animate-ping" style={{ backgroundColor: modeColor }} />
                  </div>
                </div>
              )}
            </div>

            <div className="p-6 border-t border-white/10 bg-white/5">
              <div className="flex items-center gap-4">
                <input type="file" ref={fileInputRef} onChange={handleImage} className="hidden" accept="image/*" />
                <button onClick={() => fileInputRef.current?.click()} className={`text-xl opacity-50 hover:opacity-100 ${image ? 'text-pink-500 opacity-100' : ''}`}>📎</button>
                <input
                  autoFocus value={message} onChange={e => setMessage(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && sendMessage()}
                  placeholder={image ? "Visual data linked. Enter command..." : "Inject command into Matrix..."}
                  className="flex-1 bg-transparent border-b border-white/10 pb-2 outline-none focus:border-white/40 transition-all placeholder:opacity-30"
                />
                <button onClick={sendMessage} className="px-8 py-2 font-black text-xs transition-transform active:scale-95" style={{ backgroundColor: modeColor, color: '#000' }}>EXECUTE</button>
              </div>
              {image && <div className="text-[10px] mt-2 opacity-70 italic text-pink-500 animate-pulse">>> VISUAL_PAYLOAD_READY // {image.mime_type}</div>}
            </div>
          </div>
        </div>

        <div className="hidden lg:flex lg:col-span-3 flex-col gap-4">
          <div className="flex-1 border border-white/10 bg-black/60 rounded-xl overflow-hidden backdrop-blur-md">
            <SpatialMap data={mapData} />
          </div>
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

