import React from 'react';
import { Rocket, Cpu, Activity, Wifi } from 'lucide-react';

interface HeaderProps {
  uptime: string;
}

export const Header: React.FC<HeaderProps> = ({ uptime }) => {
  return (
    <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-[rgba(255,51,0,0.3)] pb-4 relative z-10">
      <div className="flex items-center gap-3">
        <div className="p-2 bg-black border border-[rgba(255,51,0,0.5)] rounded-sm shadow-[0_0_15px_rgba(255,51,0,0.3)]">
          <Rocket className="w-6 h-6 ares-text" />
        </div>
        <div>
          <h1 className="text-xl md:text-2xl font-bold tracking-widest uppercase ares-text">
            UNIVERSAL_DRAGON_GRID
          </h1>
          <div className="flex items-center gap-2 micro-label mt-1">
            <span className="flex items-center gap-1"><Cpu className="w-3 h-3" /> DRAGON_CORE_7D</span>
            <span>|</span>
            <span className="flex items-center gap-1"><Activity className="w-3 h-3" /> OPERATOR: ASLAM</span>
          </div>
        </div>
      </div>
      
      <div className="flex gap-6">
        <div className="text-right">
          <div className="micro-label">GRID_UPTIME</div>
          <div className="data-value text-lg ares-text">{uptime}</div>
        </div>
        <div className="text-right">
          <div className="micro-label">BANDWIDTH</div>
          <div className="data-value text-lg flex items-center gap-2 text-[#FF3300]">
            <Wifi className="w-4 h-4" /> 7.0 TBps
          </div>
        </div>
      </div>
    </header>
  );
};
