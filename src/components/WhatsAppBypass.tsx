import React, { useState, useEffect, useRef } from 'react';
import { MessageSquare, ShieldAlert, Zap, Terminal as TerminalIcon, Lock, Unlock, Phone } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

interface HackStep {
  id: string;
  text: string;
  status: 'PENDING' | 'ACTIVE' | 'COMPLETE' | 'FAILED';
}

export const WhatsAppBypass: React.FC = () => {
  const [phoneNumber, setPhoneNumber] = useState('');
  const [isHacking, setIsHacking] = useState(false);
  const [steps, setSteps] = useState<HackStep[]>([]);
  const [otp, setOtp] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const terminalRef = useRef<HTMLDivElement>(null);

  const hackSequence = [
    "INITIALIZING_GRID_PROXY...",
    "INTERCEPTING_SS7_SIGNAL...",
    "BYPASSING_WHATSAPP_ENCRYPTION_V3...",
    "EXTRACTING_SMS_PAYLOAD...",
    "DECRYPTING_OTP_TOKEN...",
    "ACCESS_GRANTED_BY_ARES"
  ];

  const startHack = () => {
    if (!phoneNumber || isHacking) return;
    
    setIsHacking(true);
    setOtp(null);
    setProgress(0);
    setSteps(hackSequence.map((text, i) => ({ id: String(i), text, status: i === 0 ? 'ACTIVE' : 'PENDING' })));

    let currentStep = 0;
    const interval = setInterval(() => {
      currentStep++;
      if (currentStep >= hackSequence.length) {
        clearInterval(interval);
        setOtp(Math.floor(100000 + Math.random() * 900000).toString().replace(/(\d{3})(\d{3})/, '$1-$2'));
        setIsHacking(false);
        setSteps(prev => prev.map(s => ({ ...s, status: 'COMPLETE' })));
        setProgress(100);
        
        // Trigger a global breach effect
        window.dispatchEvent(new CustomEvent('TRIGGER_7D_BREACH'));
      } else {
        setSteps(prev => prev.map((s, i) => {
          if (i < currentStep) return { ...s, status: 'COMPLETE' };
          if (i === currentStep) return { ...s, status: 'ACTIVE' };
          return s;
        }));
        setProgress((currentStep / hackSequence.length) * 100);
      }
    }, 1200);
  };

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [steps]);

  return (
    <div className="glass-panel p-4 flex flex-col gap-4 h-full relative overflow-hidden">
      <div className="flex items-center justify-between z-10">
        <h2 className="micro-label flex items-center gap-2 text-[#00FFCC]">
          <MessageSquare className="w-4 h-4" /> WHATSAPP_OTP_BYPASS
        </h2>
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${isHacking ? 'bg-[#00FFCC] animate-pulse' : 'bg-[#333]'}`} />
          <span className="text-[10px] font-mono text-[#00FFCC]">ARES_MODULE_V4</span>
        </div>
      </div>

      <div className="space-y-3 z-10">
        <div className="relative">
          <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#444]" />
          <input 
            type="text" 
            placeholder="+1 (XXX) XXX-XXXX"
            value={phoneNumber}
            onChange={(e) => setPhoneNumber(e.target.value)}
            disabled={isHacking}
            className="w-full bg-black/50 border border-[#222] rounded py-2 pl-10 pr-4 text-[12px] font-mono text-[#00FFCC] focus:border-[#00FFCC]/50 outline-none transition-all placeholder:text-[#222]"
          />
        </div>

        <button 
          onClick={startHack}
          disabled={isHacking || !phoneNumber}
          className={`
            w-full py-2 rounded font-mono text-[10px] uppercase tracking-widest transition-all
            ${isHacking ? 'bg-[#00FFCC]/10 text-[#00FFCC] border border-[#00FFCC]/30 cursor-wait' : 'bg-[#00FFCC]/20 text-[#00FFCC] border border-[#00FFCC]/50 hover:bg-[#00FFCC]/30'}
            disabled:opacity-30
          `}
        >
          {isHacking ? 'BYPASSING_ENCRYPTION...' : 'INITIATE_OTP_EXTRACTION'}
        </button>
      </div>

      <div className="flex-1 bg-black/80 border border-[#222] rounded p-2 font-mono text-[9px] overflow-hidden flex flex-col gap-2">
        <div ref={terminalRef} className="flex-1 overflow-y-auto space-y-1 scrollbar-hide">
          {steps.map((step) => (
            <div key={step.id} className="flex items-center gap-2">
              <span className={`
                ${step.status === 'COMPLETE' ? 'text-[#00FFCC]' : 
                  step.status === 'ACTIVE' ? 'text-[#FFCC00] animate-pulse' : 
                  'text-[#333]'}
              `}>
                {step.status === 'COMPLETE' ? '[DONE]' : step.status === 'ACTIVE' ? '[RUN]' : '[WAIT]'}
              </span>
              <span className={step.status === 'ACTIVE' ? 'text-white' : 'text-[#666]'}>
                {step.text}
              </span>
            </div>
          ))}
          {otp && (
            <motion.div 
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="mt-4 p-3 bg-[#00FFCC]/10 border border-[#00FFCC]/30 rounded text-center"
            >
              <div className="text-[8px] text-[#00FFCC]/60 mb-1">INTERCEPTED_OTP_FOUND</div>
              <div className="text-xl font-bold text-[#00FFCC] tracking-[0.3em]">{otp}</div>
            </motion.div>
          )}
        </div>

        {isHacking && (
          <div className="h-1 bg-[#111] rounded-full overflow-hidden">
            <motion.div 
              className="h-full bg-[#00FFCC]"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
            />
          </div>
        )}
      </div>

      <div className="flex items-center justify-between text-[8px] font-mono text-[#444] z-10">
        <span>ENCRYPTION: AES-256-GCM</span>
        <span>STATUS: {isHacking ? 'BREACHING' : 'READY'}</span>
      </div>

      {/* Glitch Overlay during hack */}
      {isHacking && (
        <motion.div 
          animate={{ opacity: [0, 0.1, 0, 0.2, 0] }}
          transition={{ duration: 0.5, repeat: Infinity }}
          className="absolute inset-0 bg-[#00FFCC] pointer-events-none z-0"
        />
      )}
    </div>
  );
};
