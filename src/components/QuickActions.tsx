import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { 
  ShieldAlert, 
  Home, 
  RefreshCw, 
  Zap, 
  Trash2, 
  ChevronRight, 
  ChevronLeft,
  Power
} from 'lucide-react';

export const QuickActions: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  const actions = [
    { 
      id: 'emergency', 
      label: 'EMERGENCY STOP', 
      icon: <Power className="w-4 h-4" />, 
      color: 'text-[#FF3300]', 
      bg: 'bg-[#FF3300]/10',
      border: 'border-[#FF3300]/30',
      hover: 'hover:bg-[#FF3300]/20',
      onClick: () => {
        window.dispatchEvent(new CustomEvent('TRIGGER_7D_BREACH'));
        // In a real app, this would send a command to the robot
      }
    },
    { 
      id: 'home', 
      label: 'RETURN TO HOME', 
      icon: <Home className="w-4 h-4" />, 
      color: 'text-[#00FFFF]', 
      bg: 'bg-[#00FFFF]/10',
      border: 'border-[#00FFFF]/30',
      hover: 'hover:bg-[#00FFFF]/20',
      onClick: () => console.log('Returning to home...')
    },
    { 
      id: 'reboot', 
      label: 'SYSTEM REBOOT', 
      icon: <RefreshCw className="w-4 h-4" />, 
      color: 'text-[#FFCC00]', 
      bg: 'bg-[#FFCC00]/10',
      border: 'border-[#FFCC00]/30',
      hover: 'hover:bg-[#FFCC00]/20',
      onClick: () => window.location.reload()
    },
    { 
      id: 'sync', 
      label: 'GRID SYNC', 
      icon: <Zap className="w-4 h-4" />, 
      color: 'text-[#00FFCC]', 
      bg: 'bg-[#00FFCC]/10',
      border: 'border-[#00FFCC]/30',
      hover: 'hover:bg-[#00FFCC]/20',
      onClick: () => console.log('Syncing grid...')
    },
    { 
      id: 'clear', 
      label: 'CLEAR LOGS', 
      icon: <Trash2 className="w-4 h-4" />, 
      color: 'text-[#888]', 
      bg: 'bg-[#222]/10',
      border: 'border-[#222]/30',
      hover: 'hover:bg-[#222]/20',
      onClick: () => console.log('Clearing logs...')
    }
  ];

  return (
    <div className="fixed right-0 top-1/2 -translate-y-1/2 z-50 flex items-center">
      {/* Toggle Button */}
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="bg-black/80 border-y border-l border-[#222] p-2 rounded-l-md text-[#00FFFF] hover:bg-[#111] transition-all shadow-[0_0_10px_rgba(0,255,255,0.1)]"
      >
        {isOpen ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
      </button>

      {/* Panel */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 20, stiffness: 100 }}
            className="bg-black/90 border-y border-l border-[#222] p-4 rounded-l-xl shadow-[-10px_0_30px_rgba(0,0,0,0.5)] backdrop-blur-md w-64"
          >
            <div className="flex items-center gap-2 mb-4 pb-2 border-b border-[#222]">
              <ShieldAlert className="w-4 h-4 text-[#FFCC00]" />
              <span className="text-[10px] font-mono text-[#FFCC00] tracking-widest uppercase">Quick Actions</span>
            </div>

            <div className="flex flex-col gap-2">
              {actions.map((action) => (
                <button
                  key={action.id}
                  onClick={action.onClick}
                  className={`
                    flex items-center gap-3 p-3 rounded border transition-all group
                    ${action.bg} ${action.border} ${action.hover}
                  `}
                >
                  <div className={`${action.color} group-hover:scale-110 transition-transform`}>
                    {action.icon}
                  </div>
                  <span className={`text-[9px] font-mono ${action.color} tracking-wider font-bold`}>
                    {action.label}
                  </span>
                </button>
              ))}
            </div>

            <div className="mt-4 pt-2 border-t border-[#222] text-center">
              <span className="text-[8px] font-mono text-[#444] uppercase tracking-tighter">
                Master Aslam Override Active
              </span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
