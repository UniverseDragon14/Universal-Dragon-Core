import React from 'react';
import { Rocket, Cpu, Activity, Wifi } from 'lucide-react';

interface HeaderProps {
  uptime: string;
}

export const Header: React.FC<HeaderProps> = ({ uptime }) => {
  return (
    <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-[#222] pb-4">
      <div className="flex items-center gap-3">
        <div className="p-2 bg-[#111] border border-[#222] rounded-md">
          <Rocket className="w-6 h-6 neon-text" />
        </div>
        <div>
          <h1 className="text-xl md:text-2xl font-bold tracking-widest uppercase neon-text">
            Universal Dragon OS
          </h1>
          <div className="flex items-center gap-2 micro-label mt-1">
            <span className="flex items-center gap-1"><Cpu className="w-3 h-3" /> RPi 5 Core</span>
            <span>|</span>
            <span className="flex items-center gap-1"><Activity className="w-3 h-3" /> SYS_ONLINE</span>
          </div>
        </div>
      </div>
      
      <div className="flex gap-6">
        <div className="text-right">
          <div className="micro-label">Uptime</div>
          <div className="data-value text-lg">{uptime}</div>
        </div>
        <div className="text-right">
          <div className="micro-label">Network</div>
          <div className="data-value text-lg flex items-center gap-2 text-[#00FFCC]">
            <Wifi className="w-4 h-4" /> 1.2 Gbps
          </div>
        </div>
      </div>
    </header>
  );
};
