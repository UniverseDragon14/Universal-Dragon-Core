import React from 'react';
import { Terminal as TerminalIcon } from 'lucide-react';

interface TerminalProps {
  logs: string[];
}

export const Terminal: React.FC<TerminalProps> = ({ logs }) => {
  return (
    <div className="glass-panel p-4 h-48 flex flex-col">
      <h2 className="micro-label flex items-center gap-2 mb-2"><TerminalIcon className="w-4 h-4" /> System Logs</h2>
      <div className="flex-1 bg-[#050505] border border-[#222] rounded p-2 overflow-y-auto font-mono text-xs text-[#888] space-y-1">
        {logs.map((log, i) => (
          <div key={i} className={log.includes('WARN') ? 'text-[#FFCC00]' : log.includes('ERR') ? 'text-[#FF3366]' : ''}>
            {log}
          </div>
        ))}
        <div className="flex items-center gap-2 text-[#00FFCC]">
          <span>&gt;</span>
          <span className="animate-pulse">_</span>
        </div>
      </div>
    </div>
  );
};
