import React, { useEffect, useRef } from 'react';
import { Activity, AlertTriangle, ShieldAlert } from 'lucide-react';

interface SystemLogsProps {
  logs: { type: 'EVENT' | 'ERROR'; message: string; timestamp: string }[];
}

export const SystemLogs: React.FC<SystemLogsProps> = ({ logs }) => {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="glass-panel p-4 h-full flex flex-col relative overflow-hidden">
      <div className="flex items-center justify-between mb-2 z-10">
        <h2 className="micro-label flex items-center gap-2 ares-text">
          <Activity className="w-4 h-4" /> SYSTEM_LOGS_V2.0
        </h2>
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-mono text-[#00FFFF] animate-pulse">MONITORING_ACTIVE</span>
        </div>
      </div>

      <div 
        ref={scrollRef}
        className="flex-1 bg-black border border-[#222] rounded p-3 overflow-y-auto font-mono text-[10px] space-y-1 relative scrollbar-hide"
      >
        {logs.length === 0 && (
          <div className="text-[#333] text-center mt-10 italic">
            "Awaiting system telemetry..."
          </div>
        )}
        {logs.map((log, i) => (
          <div key={i} className={`flex gap-2 py-0.5 border-b border-[#111] last:border-0 ${
            log.type === 'ERROR' ? 'text-[#FF3300]' : 'text-[#00FFFF]'
          }`}>
            <span className="text-[#444] flex-shrink-0">[{log.timestamp}]</span>
            <span className="flex-shrink-0 font-bold">
              {log.type === 'ERROR' ? <AlertTriangle className="w-3 h-3 inline mr-1" /> : <ShieldAlert className="w-3 h-3 inline mr-1" />}
              {log.type}:
            </span>
            <span className="truncate">{log.message}</span>
          </div>
        ))}
      </div>

      <div className="mt-2 grid grid-cols-2 gap-2">
        <div className="bg-black/40 border border-[#222] p-1.5 rounded text-center">
          <div className="text-[8px] text-[#444] uppercase">Events</div>
          <div className="text-[10px] font-mono text-[#00FFFF]">{logs.filter(l => l.type === 'EVENT').length}</div>
        </div>
        <div className="bg-black/40 border border-[#222] p-1.5 rounded text-center">
          <div className="text-[8px] text-[#444] uppercase">Errors</div>
          <div className="text-[10px] font-mono text-[#FF3300]">{logs.filter(l => l.type === 'ERROR').length}</div>
        </div>
      </div>
    </div>
  );
};
