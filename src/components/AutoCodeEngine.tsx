import React, { useState, useEffect, useRef } from 'react';
import { Code2, Zap, RefreshCw, CheckCircle2, AlertCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

interface CodePatch {
  id: string;
  file: string;
  status: 'PATCHING' | 'VERIFYING' | 'COMPLETE' | 'FAILED';
  progress: number;
  lines: string[];
}

const MOCK_FILES = [
  'core/neural_link.ts',
  'grid/bypass_v7.sys',
  'dragon/firewall_breach.sh',
  'nova/spatial_sync.py',
  'ares/matrix_reloader.cpp',
  'master/aslam_auth.key'
];

const MOCK_CODE_SNIPPETS = [
  'const sync = await grid.connect(MASTER_KEY);',
  'if (breach.detected) return bypass.init();',
  'export function dragon_core_reboot() { ... }',
  'while (true) { neural.link.pulse(); }',
  'system.patch("ARES_V7", { force: true });',
  'import { Nova } from "@dragon/core";',
  'grid.matrix.reload({ mode: "STEALTH" });',
  'aslam.auth.verify(DRAGON_SIGNATURE);'
];

export const AutoCodeEngine: React.FC = () => {
  const [patches, setPatches] = useState<CodePatch[]>([]);
  const [activeCode, setActiveCode] = useState<string[]>([]);
  const [isInjecting, setIsInjecting] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  const handleForceRecode = () => {
    setIsInjecting(true);
    window.dispatchEvent(new CustomEvent('TRIGGER_7D_BREACH'));
    setTimeout(() => setIsInjecting(false), 2000);
    
    // Add a high-priority patch
    const newPatch: CodePatch = {
      id: 'FORCE-' + Math.random().toString(36).substr(2, 5),
      file: 'SYSTEM/OVERRIDE.EXE',
      status: 'PATCHING',
      progress: 0,
      lines: ['FORCING_GRID_RECODE...', 'BYPASSING_CORE_SECURITY...', 'MASTER_ASLAM_OVERRIDE_ACTIVE']
    };
    setPatches(prev => [newPatch, ...prev].slice(0, 5));
  };

  useEffect(() => {
    const interval = setInterval(() => {
      setPatches(prev => {
        // Update existing patches
        const updated = prev.map(p => {
          if (p.status === 'COMPLETE' || p.status === 'FAILED') return p;
          
          const nextProgress = p.progress + Math.random() * 15;
          let nextStatus = p.status;
          
          if (nextProgress >= 100) {
            nextStatus = Math.random() > 0.1 ? 'COMPLETE' : 'FAILED';
            return { ...p, progress: 100, status: nextStatus };
          } else if (nextProgress > 60) {
            nextStatus = 'VERIFYING';
          }
          
          return { ...p, progress: nextProgress, status: nextStatus };
        });

        // Add new patch if space
        if (updated.length < 4 && Math.random() > 0.7) {
          const newPatch: CodePatch = {
            id: Math.random().toString(36).substr(2, 9),
            file: MOCK_FILES[Math.floor(Math.random() * MOCK_FILES.length)],
            status: 'PATCHING',
            progress: 0,
            lines: Array.from({ length: 3 }, () => MOCK_CODE_SNIPPETS[Math.floor(Math.random() * MOCK_CODE_SNIPPETS.length)])
          };
          return [newPatch, ...updated].slice(0, 5);
        }

        return updated;
      });

      // Update background code stream
      setActiveCode(prev => {
        const newLine = MOCK_CODE_SNIPPETS[Math.floor(Math.random() * MOCK_CODE_SNIPPETS.length)];
        return [...prev.slice(-10), newLine];
      });
    }, 1500);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [activeCode]);

  return (
    <div className={`glass-panel p-4 flex flex-col gap-4 h-full relative overflow-hidden transition-all duration-300 ${isInjecting ? 'border-[#FFCC00] shadow-[0_0_20px_rgba(255,204,0,0.2)]' : ''}`}>
      {isInjecting && (
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: [0, 0.2, 0] }}
          transition={{ duration: 0.1, repeat: 20 }}
          className="absolute inset-0 bg-[#FFCC00] pointer-events-none z-0"
        />
      )}
      <div className="flex items-center justify-between z-10">
        <h2 className="micro-label flex items-center gap-2 text-[#FFCC00]">
          <Code2 className="w-4 h-4" /> AUTO_CODE_ENGINE
        </h2>
        <div className="flex items-center gap-2">
          <RefreshCw className="w-3 h-3 text-[#FFCC00] animate-spin" />
          <span className="text-[10px] font-mono text-[#FFCC00]">ENGINE_RUNNING</span>
        </div>
      </div>

      {/* Code Stream Background */}
      <div className="absolute inset-0 opacity-5 pointer-events-none font-mono text-[8px] p-4 overflow-hidden">
        {activeCode.map((line, i) => (
          <div key={i} className="whitespace-nowrap">{line}</div>
        ))}
      </div>

      <div className="flex-1 flex flex-col gap-3 z-10 overflow-hidden">
        <div className="flex-1 space-y-3 overflow-y-auto scrollbar-hide">
          <AnimatePresence initial={false}>
            {patches.map((patch) => (
              <motion.div
                key={patch.id}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="bg-black/40 border border-[#222] rounded p-2 space-y-2"
              >
                <div className="flex justify-between items-center">
                  <div className="text-[10px] font-mono text-[#888] truncate max-w-[150px]">
                    {patch.file}
                  </div>
                  <div className={`text-[9px] font-mono flex items-center gap-1
                    ${patch.status === 'COMPLETE' ? 'text-[#00FFCC]' : 
                      patch.status === 'FAILED' ? 'text-[#FF3300]' : 
                      'text-[#FFCC00] animate-pulse'}
                  `}>
                    {patch.status === 'COMPLETE' ? <CheckCircle2 className="w-3 h-3" /> : 
                     patch.status === 'FAILED' ? <AlertCircle className="w-3 h-3" /> : 
                     <Zap className="w-3 h-3" />}
                    {patch.status}
                  </div>
                </div>

                <div className="h-1 bg-[#111] rounded-full overflow-hidden">
                  <motion.div 
                    className={`h-full ${
                      patch.status === 'COMPLETE' ? 'bg-[#00FFCC]' : 
                      patch.status === 'FAILED' ? 'bg-[#FF3300]' : 
                      'bg-[#FFCC00]'
                    }`}
                    initial={{ width: 0 }}
                    animate={{ width: `${patch.progress}%` }}
                  />
                </div>

                <div className="font-mono text-[9px] text-[#444] space-y-0.5">
                  {patch.lines.map((line, i) => (
                    <div key={i} className="truncate opacity-60">
                      {patch.status === 'PATCHING' ? `> PATCHING: ${line}` : `> VERIFIED: ${line}`}
                    </div>
                  ))}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </div>

      <div className="bg-black/60 border border-[#222] p-2 rounded z-10 space-y-2">
        <div className="flex justify-between items-center text-[9px] font-mono">
          <span className="text-[#444]">ENGINE_LOAD:</span>
          <span className="text-[#FFCC00]">{(Math.random() * 20 + 10).toFixed(1)}%</span>
        </div>
        <div className="flex justify-between items-center text-[9px] font-mono">
          <span className="text-[#444]">ACTIVE_PATCHES:</span>
          <span className="text-[#FFCC00]">{patches.filter(p => p.status !== 'COMPLETE').length}</span>
        </div>
        <button 
          onClick={handleForceRecode}
          disabled={isInjecting}
          className="w-full py-1.5 bg-[#FFCC00]/10 border border-[#FFCC00]/30 rounded text-[9px] font-mono text-[#FFCC00] hover:bg-[#FFCC00]/20 transition-all uppercase tracking-widest disabled:opacity-50"
        >
          {isInjecting ? 'Injecting Code...' : 'Force Recode Grid'}
        </button>
      </div>
    </div>
  );
};
