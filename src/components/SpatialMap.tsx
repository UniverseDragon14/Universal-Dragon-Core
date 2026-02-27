import React from 'react';
import { Globe, Navigation } from 'lucide-react';
import { ResponsiveContainer, ScatterChart, XAxis, YAxis, ZAxis, Scatter } from 'recharts';
import { MapPoint } from '../types';

interface SpatialMapProps {
  data: MapPoint[];
}

export const SpatialMap: React.FC<SpatialMapProps> = ({ data }) => {
  return (
    <div className="glass-panel p-4 flex-1 flex flex-col relative overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(0,255,204,0.05)_0%,transparent_70%)] pointer-events-none"></div>
      
      <div className="flex items-center justify-between mb-2 z-10">
        <h2 className="micro-label flex items-center gap-2"><Globe className="w-4 h-4" /> Spatial Mapping (Universe Expansion)</h2>
        <div className="flex gap-2">
          <span className="px-2 py-1 bg-[#222] text-[10px] uppercase font-mono rounded text-[#00FFCC]">Lidar Active</span>
          <span className="px-2 py-1 bg-[#222] text-[10px] uppercase font-mono rounded">SLAM Sync</span>
        </div>
      </div>

      <div className="flex-1 min-h-[300px] relative border border-[#222] rounded bg-[#050505] mt-2">
        <div className="absolute inset-0 border-2 border-[#00FFCC]/20 rounded-full m-8 pointer-events-none"></div>
        <div className="absolute inset-0 border border-[#00FFCC]/10 rounded-full m-24 pointer-events-none"></div>
        <div className="absolute top-1/2 left-0 right-0 h-px bg-[#00FFCC]/20 pointer-events-none"></div>
        <div className="absolute left-1/2 top-0 bottom-0 w-px bg-[#00FFCC]/20 pointer-events-none"></div>
        
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
            <XAxis type="number" dataKey="x" hide domain={[-100, 100]} />
            <YAxis type="number" dataKey="y" hide domain={[-100, 100]} />
            <ZAxis type="number" dataKey="z" range={[10, 50]} />
            <Scatter name="Anomalies" data={data} fill="#00FFCC" opacity={0.6} isAnimationActive={false} />
          </ScatterChart>
        </ResponsiveContainer>

        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
          <Navigation className="w-6 h-6 text-[#FFCC00] animate-pulse" />
        </div>
      </div>
    </div>
  );
};
