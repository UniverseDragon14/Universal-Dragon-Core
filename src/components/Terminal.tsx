import React, { useEffect, useRef } from 'react';
import { Terminal as TerminalIcon, Flame } from 'lucide-react';

interface TerminalProps {
  logs: string[];
}

export const Terminal: React.FC<TerminalProps> = ({ logs }) => {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="glass-panel p-4 h-full flex flex-col relative overflow-hidden">
      <div className="absolute top-0 right-0 p-2 opacity-10 pointer-events-none">
        <Flame className="w-24 h-24 text-[#FF3300]" />
      </div>

      <div className="flex items-center justify-between mb-2 z-10">
        <h2 className="micro-label flex items-center gap-2 ares-text">
          <TerminalIcon className="w-4 h-4" /> DRAGON_INTERFACE_V7.0
        </h2>
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-mono text-[#FF3300] animate-pulse">OPERATOR: ASLAM</span>
        </div>
      </div>

      <div 
        ref={scrollRef}
        className="flex-1 bg-black border border-[#222] rounded p-3 overflow-y-auto font-mono text-[11px] text-[#888] space-y-1 relative"
      >
        <div className="text-[#FF3300] mb-4 leading-none whitespace-pre">
{`   🔥  🔥  🔥  [ WARNING: DRAGON_GRID_BREACH ]  🔥  🔥  🔥
      (X_X)  SECURITY_BYPASSED_BY_MASTER_ASLAM  (X_X)
     ~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~`}
        </div>

        {logs.map((log, i) => (
          <div key={i} className={`
            ${log.includes('WARN') ? 'text-[#FFCC00]' : ''}
            ${log.includes('ERR') || log.includes('BREACH') ? 'text-[#FF3300]' : ''}
            ${log.includes('NOVA') ? 'text-[#00FFFF]' : ''}
            ${log.includes('DRAGON_EYE') ? 'ares-text font-bold' : ''}
          `}>
            <span className="text-[#444] mr-2">[{new Date().toLocaleTimeString().split(' ')[0]}]</span>
            {log}
          </div>
        ))}
        
        <div className="flex items-center gap-2 text-[#00FFFF] mt-2">
          <span>ARES_PROMPT &gt;</span>
          <span className="animate-pulse">_</span>
        </div>
      </div>
    </div>
  );
};
