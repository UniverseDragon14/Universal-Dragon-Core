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
    <div className="flex flex-col gap-6">
      <div className="glass-panel p-4 flex-1">
        <div className="flex items-center justify-between mb-4">
          <h2 className="micro-label flex items-center gap-2"><Cpu className="w-4 h-4" /> Core Telemetry</h2>
          <span className="w-2 h-2 rounded-full bg-[#00FFCC] animate-pulse"></span>
        </div>
        
        <div className="space-y-6">
          <div>
            <div className="flex justify-between mb-1">
              <span className="micro-label">CPU Usage</span>
              <span className="data-value text-sm">{latest.usage}%</span>
            </div>
            <div className="h-1.5 w-full bg-[#222] rounded-full overflow-hidden">
              <div 
                className="h-full bg-[#00FFCC] transition-all duration-500" 
                style={{ width: `${latest.usage}%` }}
              ></div>
            </div>
          </div>

          <div>
            <div className="flex justify-between mb-1">
              <span className="micro-label">Memory (8GB)</span>
              <span className="data-value text-sm">4.2 GB</span>
            </div>
            <div className="h-1.5 w-full bg-[#222] rounded-full overflow-hidden">
              <div className="h-full bg-[#FFCC00] w-[52%]"></div>
            </div>
          </div>

          <div>
            <div className="flex justify-between mb-1">
              <span className="micro-label">Core Temp</span>
              <span className={`data-value text-sm ${latest.temp > 60 ? 'danger-text' : ''}`}>
                {latest.temp}°C
              </span>
            </div>
            <div className="h-1.5 w-full bg-[#222] rounded-full overflow-hidden">
              <div 
                className={`h-full transition-all duration-500 ${latest.temp > 60 ? 'bg-[#FF3366]' : 'bg-[#00FFCC]'}`}
                style={{ width: `${(latest.temp / 85) * 100}%` }}
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
        <h2 className="micro-label flex items-center gap-2 mb-4"><Battery className="w-4 h-4" /> Power Systems</h2>
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-[#0a0a0a] p-3 rounded border border-[#222]">
            <div className="micro-label mb-1">Main Cell</div>
            <div className="data-value text-xl text-[#00FFCC]">87%</div>
            <div className="micro-label mt-1 text-[10px]">Discharging</div>
          </div>
          <div className="bg-[#0a0a0a] p-3 rounded border border-[#222]">
            <div className="micro-label mb-1">Draw</div>
            <div className="data-value text-xl">12.4W</div>
            <div className="micro-label mt-1 text-[10px]">Nominal</div>
          </div>
        </div>
      </div>
    </div>
  );
};
