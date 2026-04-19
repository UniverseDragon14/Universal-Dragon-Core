import React, { useState, useEffect } from 'react';
import { io } from 'socket.io-client';
import { 
  Zap, ShieldAlert, Cpu, Terminal as TerminalIcon, 
  Flame, Radio, Database
} from 'lucide-react';
import { motion } from 'motion/react';

export const NovaCore: React.FC = () => {
  const [isBreaching, setIsBreaching] = useState(false);
  const [isVisionActive, setIsVisionActive] = useState(false);
  const [syncLevel, setSyncLevel] = useState(94);

  const triggerBreach = () => {
    setIsBreaching(true);
    setTimeout(() => setIsBreaching(false), 3000);
  };

  useEffect(() => {
    const socket = io();
    socket.on('dragon_eye_detection', () => {
      setIsVisionActive(true);
      setTimeout(() => setIsVisionActive(false), 1000);
    });
    return () => {
      socket.disconnect();
    };
  }, []);

  useEffect(() => {
    const handleBreachEvent = () => triggerBreach();
    window.addEventListener('TRIGGER_7D_BREACH', handleBreachEvent);
    return () => window.removeEventListener('TRIGGER_7D_BREACH', handleBreachEvent);
  }, []);

  return (
    <div className="glass-panel p-4 flex flex-col gap-4 relative overflow-hidden">
      {isBreaching && (
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: [0, 0.4, 0] }}
          transition={{ duration: 0.2, repeat: 15 }}
          className="absolute inset-0 bg-[#FF3300] pointer-events-none z-0"
        />
      )}

      <div className="flex items-center justify-between z-10">
        <h2 className="micro-label flex items-center gap-2 ares-text">
          <Flame className={`w-4 h-4 ${isVisionActive ? 'text-[#00FFFF] animate-pulse' : 'text-[#FF3300]'}`} /> DRAGON 7D Core
        </h2>
        <div className="flex items-center gap-2">
          <span className={`text-[10px] font-mono ${isVisionActive ? 'text-[#00FFFF]' : 'text-[#FF3300]'} animate-pulse`}>
            {isVisionActive ? 'GRID_SYNC' : 'ARES_ACTIVE'}
          </span>
        </div>
      </div>

      <div className="bg-black border border-[#FF3300]/30 rounded p-4 flex flex-col items-center justify-center gap-4 relative">
        <div className="relative">
          <motion.div 
            animate={{ rotate: 360 }}
            transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
            className="w-24 h-24 border-2 border-dashed border-[#FF3300]/50 rounded-full shadow-[0_0_20px_rgba(255,51,0,0.2)]"
          />
          <motion.div 
            animate={{ rotate: -360 }}
            transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
            className="absolute inset-0 w-24 h-24 border border-dotted border-[#00FFFF]/30 rounded-full m-2"
          />
          <div className="absolute inset-0 flex items-center justify-center overflow-hidden rounded-full p-4">
            <img 
              src="https://img.icons8.com/ios-filled/200/00FFFF/dragon.png" 
              alt="Universal Dragon" 
              className={`w-16 h-16 object-contain ${isBreaching ? 'brightness-50 sepia-[1] hue-rotate-[-50deg] saturate-[5]' : ''} transition-all drop-shadow-[0_0_10px_rgba(0,255,255,0.8)]`}
              referrerPolicy="no-referrer"
            />
          </div>
        </div>

        <div className="text-center">
          <div className="micro-label text-[10px] text-[#888]">Grid Synchronization</div>
          <div className="data-value text-2xl ares-text">{syncLevel}%</div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-2 z-10">
        <div className="bg-black/50 border border-[rgba(255,51,0,0.2)] p-2 rounded">
          <div className="micro-label text-[8px]">Ares Injection</div>
          <div className="text-[10px] font-mono text-[#00FFFF]">ACTIVE</div>
        </div>
        <div className="bg-black/50 border border-[rgba(255,51,0,0.2)] p-2 rounded">
          <div className="micro-label text-[8px]">Grid Bypass</div>
          <div className="text-[10px] font-mono text-[#FFCC00]">STABLE</div>
        </div>
      </div>

      <button 
        onClick={triggerBreach}
        disabled={isBreaching}
        className="w-full py-2 bg-[#FF3300]/10 border border-[#FF3300]/50 rounded micro-label hover:bg-[#FF3300]/20 transition-all disabled:opacity-50 ares-text"
      >
        {isBreaching ? 'BREACHING_GRID...' : 'INITIATE_ARES_BREACH'}
      </button>

      <div className="mt-2 text-[9px] font-mono text-[#555] flex flex-col gap-1">
        <div className="flex justify-between">
          <span>CREATOR:</span>
          <span className="text-[#888]">ASLAM</span>
        </div>
        <div className="flex justify-between">
          <span>MASTER:</span>
          <span className="text-[#888]">ASLAM_REAL_CREATOR</span>
        </div>
      </div>
    </div>
  );
};
