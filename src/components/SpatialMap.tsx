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
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(255,51,102,0.05)_0%,transparent_70%)] pointer-events-none"></div>
      
      <div className="flex items-center justify-between mb-2 z-10">
        <h2 className="micro-label flex items-center gap-2 text-[#FF3366]"><Globe className="w-4 h-4" /> SPATIAL_RECON_7D</h2>
        <div className="flex gap-2">
          <span className="px-2 py-1 bg-[#111] text-[10px] uppercase font-mono rounded text-[#FF3366] border border-[#FF3366]/20">LIDAR_ACTIVE</span>
          <span className="px-2 py-1 bg-[#111] text-[10px] uppercase font-mono rounded text-[#00FFCC] border border-[#00FFCC]/20">SLAM_SYNC</span>
        </div>
      </div>

      <div className="flex-1 min-h-[300px] relative border border-[#222] rounded bg-[#050505] mt-2 overflow-hidden">
        <div className="absolute inset-0 border-2 border-[#FF3366]/10 rounded-full m-8 pointer-events-none animate-pulse"></div>
        <div className="absolute inset-0 border border-[#FF3366]/5 rounded-full m-24 pointer-events-none"></div>
        <div className="absolute top-1/2 left-0 right-0 h-px bg-[#FF3366]/10 pointer-events-none"></div>
        <div className="absolute left-1/2 top-0 bottom-0 w-px bg-[#FF3366]/10 pointer-events-none"></div>
        
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
            <XAxis type="number" dataKey="x" hide domain={[-100, 100]} />
            <YAxis type="number" dataKey="y" hide domain={[-100, 100]} />
            <ZAxis type="number" dataKey="z" range={[10, 50]} />
            <Scatter name="Anomalies" data={data.filter(p => !p.isDetection)} fill="#FF3366" opacity={0.6} isAnimationActive={false} />
            <Scatter name="Detections" data={data.filter(p => p.isDetection)} fill="#00FFCC" opacity={0.9} isAnimationActive={false} />
          </ScatterChart>
        </ResponsiveContainer>

        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
          <Navigation className="w-6 h-6 text-[#FFCC00] animate-pulse drop-shadow-[0_0_10px_#FFCC00]" />
        </div>
        
        <div className="absolute bottom-2 right-2 text-[8px] font-mono text-[#333]">
          UNIVERSAL_DRAGON_GRID // CREATOR: ASLAM
        </div>
      </div>
    </div>
  );
};
