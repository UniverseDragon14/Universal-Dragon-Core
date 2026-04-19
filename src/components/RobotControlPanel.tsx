import React, { useState } from 'react';
import { 
  ChevronUp, ChevronDown, ChevronLeft, ChevronRight, 
  Square, Zap, Lightbulb, Radar, Cpu,
  Move
} from 'lucide-react';
import { motion } from 'motion/react';

export const RobotControlPanel: React.FC = () => {
  const [speed, setSpeed] = useState(0);
  const [armElevation, setArmElevation] = useState(0);
  const [activeControls, setActiveControls] = useState<Record<string, boolean>>({
    lights: false,
    scanner: false,
    auto: false
  });

  const toggleControl = (key: string) => {
    setActiveControls(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const ControlButton = ({ icon: Icon, label, onClick, active = false, danger = false }: any) => (
    <motion.button
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      onClick={onClick}
      className={`
        flex flex-col items-center justify-center p-4 rounded-lg border transition-all duration-200
        ${active 
          ? 'bg-[#FF3366]/20 border-[#FF3366] text-[#FF3366] shadow-[0_0_15px_rgba(255,51,102,0.2)]' 
          : 'bg-[#0a0a0a] border-[#222] text-[#888] hover:border-[#FF3366] hover:text-[#FF3366]'}
        ${danger && !active ? 'hover:border-[#FF3366] hover:text-[#FF3366]' : ''}
      `}
    >
      <Icon className="w-6 h-6 mb-2" />
      <span className="micro-label text-[10px]">{label}</span>
    </motion.button>
  );

  return (
    <div className="flex flex-col gap-6 h-full relative overflow-hidden">
      <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-[#FF3366] to-transparent opacity-30" />
      
      {/* Movement Controls */}
      <div className="glass-panel p-4 relative">
        <div className="absolute top-2 right-4 text-[10px] font-mono text-[#444]">AUTH: MASTER ASLAM</div>
        <h2 className="micro-label flex items-center gap-2 mb-6 text-[#FF3366]">
          <Move className="w-4 h-4" /> KINETIC_MATRIX
        </h2>
        
        <div className="grid grid-cols-3 gap-2 max-w-[200px] mx-auto">
          <div />
          <ControlButton icon={ChevronUp} label="FWD" />
          <div />
          
          <ControlButton icon={ChevronLeft} label="LFT" />
          <ControlButton icon={Square} label="STOP" danger />
          <ControlButton icon={ChevronRight} label="RGT" />
          
          <div />
          <ControlButton icon={ChevronDown} label="BWD" />
          <div />
        </div>
      </div>

      {/* Sliders */}
      <div className="glass-panel p-4">
        <h2 className="micro-label flex items-center gap-2 mb-6 text-[#FFCC00]">
          <Zap className="w-4 h-4" /> INFERNO_CALIBRATION
        </h2>
        
        <div className="space-y-6">
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="micro-label opacity-50">VELOCITY_LIMIT</span>
              <span className="data-value text-[#FF3366]">{speed}%</span>
            </div>
            <input 
              type="range" 
              min="0" 
              max="100" 
              value={speed} 
              onChange={(e) => setSpeed(parseInt(e.target.value))}
              className="w-full h-1 bg-[#222] rounded-lg appearance-none cursor-pointer accent-[#FF3366]"
            />
          </div>

          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="micro-label opacity-50">ARM_ELEVATION</span>
              <span className="data-value text-[#00FFCC]">{armElevation}°</span>
            </div>
            <input 
              type="range" 
              min="0" 
              max="90" 
              value={armElevation} 
              onChange={(e) => setArmElevation(parseInt(e.target.value))}
              className="w-full h-1 bg-[#222] rounded-lg appearance-none cursor-pointer accent-[#00FFCC]"
            />
          </div>
        </div>
      </div>

      {/* System Toggles */}
      <div className="glass-panel p-4 flex-1">
        <h2 className="micro-label flex items-center gap-2 mb-6 text-[#00FFCC]">
          <Cpu className="w-4 h-4" /> 7D_SUBSYSTEMS
        </h2>
        
        <div className="grid grid-cols-2 gap-3">
          <ControlButton 
            icon={Lightbulb} 
            label="PHOTON_ARRAY" 
            active={activeControls.lights}
            onClick={() => toggleControl('lights')}
          />
          <ControlButton 
            icon={Radar} 
            label="DEEP_SCAN" 
            active={activeControls.scanner}
            onClick={() => toggleControl('scanner')}
          />
          <div className="col-span-2">
            <motion.button
              whileTap={{ scale: 0.98 }}
              onClick={() => toggleControl('auto')}
              className={`
                w-full py-3 rounded border flex items-center justify-center gap-3 transition-all
                ${activeControls.auto 
                  ? 'bg-[#FF3366]/10 border-[#FF3366] text-[#FF3366] shadow-[0_0_20px_rgba(255,51,102,0.1)]' 
                  : 'bg-[#0a0a0a] border-[#222] text-[#888] hover:border-[#FF3366]'}
              `}
            >
              <div className={`w-2 h-2 rounded-full ${activeControls.auto ? 'bg-[#FF3366] animate-pulse' : 'bg-[#444]'}`} />
              <span className="micro-label">BREACH_PROTOCOL_7D</span>
            </motion.button>
          </div>
        </div>
      </div>
    </div>
  );
};
