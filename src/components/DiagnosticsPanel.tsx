import React, { useState, useEffect } from 'react';
import { 
  Activity, AlertTriangle, CheckCircle2, 
  Settings, RefreshCw, ShieldCheck, 
  HardDrive, Cpu, Radio, Zap
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

interface Subsystem {
  id: string;
  name: string;
  icon: any;
  status: 'nominal' | 'warning' | 'critical';
  message: string;
  load: number;
}

export const DiagnosticsPanel: React.FC = () => {
  const [isScanning, setIsScanning] = useState(false);
  const [lastCheck, setLastCheck] = useState(new Date().toLocaleTimeString());
  const [subsystems, setSubsystems] = useState<Subsystem[]>([
    { id: 'prop', name: 'KINETIC_DRIVE', icon: Zap, status: 'nominal', message: 'All drives synced', load: 12 },
    { id: 'vis', name: 'SPATIAL_RECON', icon: Radio, status: 'nominal', message: 'Clear visibility', load: 45 },
    { id: 'pow', name: 'POWER_FLUX', icon: Activity, status: 'warning', message: 'Cell 3 imbalance', load: 88 },
    { id: 'log', name: '7D_LOGIC_CORE', icon: Cpu, status: 'nominal', message: 'Stable processing', load: 24 },
    { id: 'stor', name: 'DATA_VAULT', icon: HardDrive, status: 'nominal', message: '92% capacity free', load: 8 },
  ]);

  const runDiagnostics = () => {
    setIsScanning(true);
    setTimeout(() => {
      setIsScanning(false);
      setLastCheck(new Date().toLocaleTimeString());
      // Randomize statuses slightly for effect
      setSubsystems(prev => prev.map(s => ({
        ...s,
        status: Math.random() > 0.8 ? 'warning' : 'nominal',
        load: Math.floor(Math.random() * 100)
      })));
    }, 2000);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'nominal': return 'text-[#00FFCC]';
      case 'warning': return 'text-[#FFCC00]';
      case 'critical': return 'text-[#FF3366]';
      default: return 'text-[#888]';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'nominal': return <CheckCircle2 className="w-4 h-4 text-[#00FFCC] shadow-[0_0_5px_#00FFCC]" />;
      case 'warning': return <AlertTriangle className="w-4 h-4 text-[#FFCC00] animate-pulse" />;
      case 'critical': return <ShieldCheck className="w-4 h-4 text-[#FF3366] shadow-[0_0_5px_#FF3366]" />;
      default: return null;
    }
  };

  return (
    <div className="glass-panel p-4 flex flex-col h-full relative overflow-hidden">
      <div className="absolute top-0 right-0 p-2 opacity-5 pointer-events-none">
        <Activity className="w-32 h-32 text-[#FF3366]" />
      </div>
      
      <div className="flex items-center justify-between mb-4">
        <h2 className="micro-label flex items-center gap-2 text-[#FF3366]">
          <Settings className="w-4 h-4" /> SYSTEM_INTEGRITY_7D
        </h2>
        <button 
          onClick={runDiagnostics}
          disabled={isScanning}
          className="p-1.5 rounded bg-[#111] border border-[#222] hover:bg-[#222] transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-3 h-3 text-[#FF3366] ${isScanning ? 'animate-spin' : ''}`} />
        </button>
      </div>

      <div className="flex-1 space-y-3 overflow-y-auto pr-1">
        <AnimatePresence mode="popLayout">
          {subsystems.map((sub) => (
            <motion.div 
              key={sub.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              className="bg-[#050505] border border-[#222] rounded p-3 relative overflow-hidden group hover:border-[#FF3366]/50 transition-colors"
            >
              {isScanning && (
                <motion.div 
                  initial={{ left: '-100%' }}
                  animate={{ left: '100%' }}
                  transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
                  className="absolute top-0 bottom-0 w-1/2 bg-gradient-to-r from-transparent via-[#FF3366]/5 to-transparent skew-x-12 pointer-events-none"
                />
              )}
              
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-3">
                  <div className={`p-1.5 rounded bg-[#111] border border-[#222] ${getStatusColor(sub.status)}`}>
                    <sub.icon className="w-4 h-4" />
                  </div>
                  <div>
                    <div className="text-xs font-bold uppercase tracking-wider group-hover:text-[#FF3366] transition-colors">{sub.name}</div>
                    <div className="text-[10px] text-[#444] font-mono">{sub.message}</div>
                  </div>
                </div>
                {getStatusIcon(sub.status)}
              </div>

              <div className="flex items-center gap-3">
                <div className="flex-1 h-1 bg-[#111] rounded-full overflow-hidden border border-[#222]">
                  <motion.div 
                    initial={{ width: 0 }}
                    animate={{ width: `${sub.load}%` }}
                    className={`h-full ${sub.load > 80 ? 'bg-[#FF3366] shadow-[0_0_5px_#FF3366]' : 'bg-[#00FFCC] shadow-[0_0_5px_#00FFCC]'}`}
                  />
                </div>
                <span className="data-value text-[10px] min-w-[24px] text-right text-[#444]">{sub.load}%</span>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      <div className="mt-4 pt-4 border-t border-[#222] flex justify-between items-center">
        <div className="micro-label text-[9px] opacity-50">LAST_INTEGRITY_CHECK</div>
        <div className="data-value text-[10px] text-[#FFCC00]">{lastCheck}</div>
      </div>
    </div>
  );
};
