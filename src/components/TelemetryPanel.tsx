import React from 'react';
import { Cpu, Battery } from 'lucide-react';
import { ResponsiveContainer, LineChart, Line } from 'recharts';
import { TelemetryData } from '../types';

interface TelemetryPanelProps {
  data: TelemetryData[];
}

export const TelemetryPanel: React.FC<TelemetryPanelProps> = ({ data }) => {
  const latest = data[data.length - 1] || { usage: 0, temp: 0 };
  
  return (
    <div className="flex flex-col gap-6 h-full">
      <div className="glass-panel p-4 flex-1 relative overflow-hidden">
        <div className="absolute top-0 right-0 p-2 text-[8px] font-mono text-[#333] pointer-events-none">
          7D_DRAGON_OS_TELEMETRY
        </div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="micro-label flex items-center gap-2 text-[#FF3366]"><Cpu className="w-4 h-4" /> CORE_TELEMETRY</h2>
          <span className="w-2 h-2 rounded-full bg-[#FF3366] animate-pulse shadow-[0_0_10px_#FF3366]"></span>
        </div>
        
        <div className="space-y-6">
          <div>
            <div className="flex justify-between mb-1">
              <span className="micro-label opacity-50">CPU_LOAD</span>
              <span className="data-value text-sm text-[#00FFCC]">{latest.usage}%</span>
            </div>
            <div className="h-1.5 w-full bg-[#111] rounded-full overflow-hidden border border-[#222]">
              <div 
                className="h-full bg-[#00FFCC] transition-all duration-500 shadow-[0_0_10px_#00FFCC]" 
                style={{ width: `${latest.usage}%` }}
              ></div>
            </div>
          </div>

          <div>
            <div className="flex justify-between mb-1">
              <span className="micro-label opacity-50">PWR_FLUX</span>
              <span className="data-value text-sm text-[#FFCC00]">-- GB</span>
            </div>
            <div className="h-1.5 w-full bg-[#111] rounded-full overflow-hidden border border-[#222]">
              <div className="h-full bg-[#FFCC00] w-0 shadow-[0_0_10px_#FFCC00]"></div>
            </div>
          </div>

          <div>
            <div className="flex justify-between mb-1">
              <span className="micro-label opacity-50">CORE_TEMP</span>
              <span className={`data-value text-sm ${latest.temp > 60 ? 'text-[#FF3366]' : 'text-[#00FFCC]'}`}>
                {latest.temp > 0 ? `${latest.temp}°C` : '--°C'}
              </span>
            </div>
            <div className="h-1.5 w-full bg-[#111] rounded-full overflow-hidden border border-[#222]">
              <div 
                className={`h-full transition-all duration-500 ${latest.temp > 60 ? 'bg-[#FF3366] shadow-[0_0_10px_#FF3366]' : 'bg-[#00FFCC] shadow-[0_0_10px_#00FFCC]'}`}
                style={{ width: `${latest.temp > 0 ? (latest.temp / 85) * 100 : 0}%` }}
              ></div>
            </div>
          </div>
        </div>

        <div className="mt-6 h-32">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <Line type="monotone" dataKey="usage" stroke="#00FFCC" strokeWidth={2} dot={false} isAnimationActive={false} />
              <Line type="monotone" dataKey="temp" stroke="#FF3366" strokeWidth={2} dot={false} isAnimationActive={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="glass-panel p-4">
        <h2 className="micro-label flex items-center gap-2 mb-4 text-[#FFCC00]"><Battery className="w-4 h-4" /> POWER_SYSTEMS</h2>
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-[#050505] p-3 rounded border border-[#222]">
            <div className="micro-label mb-1 opacity-50">MAIN_CELL</div>
            <div className="data-value text-xl text-[#00FFCC]">--%</div>
            <div className="micro-label mt-1 text-[10px] text-[#444]">STANDBY</div>
          </div>
          <div className="bg-[#050505] p-3 rounded border border-[#222]">
            <div className="micro-label mb-1 opacity-50">DRAW</div>
            <div className="data-value text-xl text-[#FFCC00]">--W</div>
            <div className="micro-label mt-1 text-[10px] text-[#00FFCC]">NOMINAL</div>
          </div>
        </div>
      </div>
    </div>
  );
};
