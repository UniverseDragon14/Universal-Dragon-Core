import React from 'react';
import { Zap, Crosshair, ShieldAlert, Activity } from 'lucide-react';

export const ControlPanel: React.FC = () => {
  return (
    <div className="flex flex-col gap-6 h-full">
      <div className="glass-panel p-4">
        <h2 className="micro-label flex items-center gap-2 mb-4"><Zap className="w-4 h-4" /> Motor Control</h2>
        
        <div className="space-y-4">
          {['Front Left', 'Front Right', 'Rear Left', 'Rear Right'].map((motor) => (
            <div key={motor} className="bg-[#0a0a0a] p-3 rounded border border-[#222]">
              <div className="flex justify-between items-center mb-2">
                <span className="micro-label">{motor}</span>
                <span className="data-value text-xs text-[#00FFCC]">{Math.floor(Math.random() * 20 + 80)} RPM</span>
              </div>
              <div className="h-1 w-full bg-[#222] rounded-full overflow-hidden">
                <div className="h-full bg-[#00FFCC]" style={{ width: `${Math.random() * 40 + 60}%` }}></div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="glass-panel p-4 flex-1">
        <h2 className="micro-label flex items-center gap-2 mb-4"><Crosshair className="w-4 h-4" /> Sensors & Actuators</h2>
        
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-[#0a0a0a] p-3 rounded border border-[#222] text-center">
            <ShieldAlert className="w-5 h-5 mx-auto mb-2 text-[#00FFCC]" />
            <div className="micro-label">Proximity</div>
            <div className="data-value text-sm mt-1">CLEAR</div>
          </div>
          <div className="bg-[#0a0a0a] p-3 rounded border border-[#222] text-center">
            <Activity className="w-5 h-5 mx-auto mb-2 text-[#FFCC00]" />
            <div className="micro-label">Gyroscope</div>
            <div className="data-value text-sm mt-1">STABLE</div>
          </div>
          <div className="bg-[#0a0a0a] p-3 rounded border border-[#222] text-center col-span-2">
            <div className="micro-label mb-2 text-left">Manipulator Arm</div>
            <div className="flex justify-between items-center">
              <span className="text-xs text-[#888]">Status</span>
              <span className="data-value text-sm text-[#00FFCC]">IDLE</span>
            </div>
            <div className="flex justify-between items-center mt-1">
              <span className="text-xs text-[#888]">Load</span>
              <span className="data-value text-sm">0.0 kg</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
