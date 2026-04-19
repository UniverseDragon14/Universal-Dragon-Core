import React from 'react';
import { 
  Target, Battery, MapPin, HeartPulse, 
  ChevronRight 
} from 'lucide-react';

interface StatusItemProps {
  icon: any;
  label: string;
  value: string;
  subValue?: string;
  color?: string;
}

const StatusItem: React.FC<StatusItemProps> = ({ icon: Icon, label, value, subValue, color = "text-[#00FFCC]" }) => (
  <div className="bg-[#050505] border border-[#222] rounded p-3 flex items-center gap-3 group hover:border-[#FF3366]/50 transition-colors">
    <div className={`p-2 rounded bg-[#111] border border-[#222] ${color} group-hover:shadow-[0_0_10px_currentColor] transition-all`}>
      <Icon className="w-4 h-4" />
    </div>
    <div className="flex-1 min-w-0">
      <div className="micro-label text-[9px] mb-0.5 opacity-50 group-hover:text-[#FF3366] transition-colors">{label}</div>
      <div className="flex items-baseline gap-2">
        <div className="data-value text-xs truncate">{value}</div>
        {subValue && <div className="text-[9px] text-[#444] font-mono">{subValue}</div>}
      </div>
    </div>
    <ChevronRight className="w-3 h-3 text-[#333] group-hover:text-[#FF3366] transition-colors" />
  </div>
);

export const RobotStatusSummary: React.FC = () => {
  return (
    <div className="glass-panel p-4 flex flex-col gap-4 relative overflow-hidden">
      <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-[#FF3366] to-transparent opacity-30" />
      <h2 className="micro-label flex items-center gap-2 text-[#FF3366]">
        <HeartPulse className="w-4 h-4" /> MISSION_STATUS_7D
      </h2>
      
      <div className="grid grid-cols-1 gap-2">
        <StatusItem 
          icon={Target} 
          label="ACTIVE_MISSION" 
          value="ARES_7D_IDLE" 
          subValue="0%_BREACHED"
          color="text-[#FF3366]"
        />
        <StatusItem 
          icon={Battery} 
          label="CORE_ENERGY" 
          value="--%" 
          subValue="--h_REMAINING"
          color="text-[#00FFCC]"
        />
        <StatusItem 
          icon={MapPin} 
          label="COORDINATES" 
          value="GRID_ORIGIN" 
          subValue="X:0 Y:0"
          color="text-[#FFCC00]"
        />
        <StatusItem 
          icon={HeartPulse} 
          label="SYSTEM_HEALTH" 
          value="STANDBY" 
          subValue="MASTER_ASLAM_SYNCED"
          color="text-[#00FFCC]"
        />
      </div>
    </div>
  );
};
