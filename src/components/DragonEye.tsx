import React, { useState, useEffect, useRef } from 'react';
import { io } from 'socket.io-client';
import { Eye, ShieldAlert, Camera, Clock, Target, Maximize2, X } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

interface Detection {
  camera: string;
  timestamp: string;
  object: string;
  confidence: number;
  bbox: number[];
  size: string;
  saved_image: string;
}

export const DragonEye: React.FC = () => {
  const [detections, setDetections] = useState<Detection[]>([]);
  const [selectedDetection, setSelectedDetection] = useState<Detection | null>(null);
  const [lastDetection, setLastDetection] = useState<Detection | null>(null);
  const [isLive, setIsLive] = useState(false);
  const [mqttStatus, setMqttStatus] = useState<{ connected: boolean; broker: string; error?: string }>({
    connected: false,
    broker: '192.168.70.196'
  });
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const socket = io();

    socket.on('connect', () => setIsLive(true));
    socket.on('disconnect', () => setIsLive(false));
    socket.on('mqtt_status', (status: any) => setMqttStatus(status));

    socket.on('dragon_eye_detection', (detection: Detection) => {
      setDetections(prev => [detection, ...prev].slice(0, 50));
      setLastDetection(detection);
      setTimeout(() => setLastDetection(null), 3000);
      
      // Auto-select if it's a high-confidence alert
      if (detection.confidence > 0.85) {
        // Optional: setSelectedDetection(detection);
      }
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = 0;
    }
  }, [detections]);

  return (
    <div className="glass-panel p-4 flex flex-col gap-4 h-full relative overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between z-10">
        <h2 className="micro-label flex items-center gap-2 ares-text">
          <Eye className="w-4 h-4" /> ARES_GRID_7D_VISION
        </h2>
        <div className="flex items-center gap-2">
          <div className="flex flex-col items-end">
            <span className={`text-[10px] font-mono ${isLive ? 'text-[#00FFFF] animate-pulse' : 'text-[#444]'}`}>
              {isLive ? 'GRID_FEED_ACTIVE' : 'OFFLINE'}
            </span>
            <span 
              className={`text-[8px] font-mono ${mqttStatus.connected ? 'text-[#00FFFF]' : 'text-[#FF3300] opacity-60'}`}
              title={mqttStatus.error || 'Broker status'}
            >
              MQTT: {mqttStatus.connected ? 'CONNECTED' : 'UNREACHABLE'}
            </span>
          </div>
        </div>
      </div>

      {/* Detection Alert Toast */}
      <AnimatePresence>
        {lastDetection && (
          <motion.div 
            initial={{ opacity: 0, y: 20, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="absolute top-12 left-4 right-4 bg-[#FF3300] text-white p-2 rounded shadow-lg z-20 flex items-center gap-3 border border-white/20"
          >
            <ShieldAlert className="w-5 h-5 animate-pulse" />
            <div className="flex-1">
              <div className="text-[8px] font-bold opacity-80 uppercase tracking-widest">ARES_VISION_ALERT</div>
              <div className="text-[10px] font-mono font-bold">{lastDetection.object.toUpperCase()} DETECTED ON {lastDetection.camera}</div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Live Monitor Area */}
      <div className="relative h-40 bg-black border border-[#FF3300]/30 rounded overflow-hidden z-10">
        <AnimatePresence mode="wait">
          {detections.length > 0 ? (
            <motion.div
              key={detections[0].timestamp}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0"
            >
              <img 
                src={detections[0].saved_image} 
                alt="Live Feed" 
                className="w-full h-full object-cover opacity-60 grayscale contrast-125"
                referrerPolicy="no-referrer"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black to-transparent opacity-40" />
              
              {/* Live Bounding Box Overlay */}
              <div 
                className="absolute border-2 border-[#FF3300] pointer-events-none shadow-[0_0_10px_rgba(255,51,0,0.5)]"
                style={{
                  left: `${(detections[0].bbox[0] / 640) * 100}%`,
                  top: `${(detections[0].bbox[1] / 480) * 100}%`,
                  width: `${((detections[0].bbox[2] - detections[0].bbox[0]) / 640) * 100}%`,
                  height: `${((detections[0].bbox[3] - detections[0].bbox[1]) / 480) * 100}%`,
                }}
              >
                <div className="absolute -top-4 left-0 bg-[#FF3300] text-white text-[8px] px-1 font-mono uppercase">
                  {detections[0].object} {Math.round(detections[0].confidence * 100)}%
                </div>
              </div>

              <div className="absolute top-2 left-2 flex items-center gap-2">
                <div className="w-2 h-2 bg-[#FF3300] rounded-full animate-pulse" />
                <span className="text-[9px] font-mono text-[#FF3300] uppercase tracking-tighter">ARES_RECON: {detections[0].camera}</span>
              </div>
            </motion.div>
          ) : (
            <div className="absolute inset-0 flex items-center justify-center">
              <img 
                src="https://img.icons8.com/ios-filled/200/FF3300/dragon.png" 
                alt="Dragon Feed" 
                className="w-32 h-32 object-contain opacity-20"
                referrerPolicy="no-referrer"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black to-transparent opacity-60" />
              <div className="absolute inset-0 flex flex-col items-center justify-center text-[#FF3300] font-mono text-[10px] z-10">
                <Camera className="w-6 h-6 mb-2 opacity-60 animate-pulse" />
                <span className="tracking-[0.2em]">DRAGON_FEED_STANDBY</span>
              </div>
            </div>
          )}
        </AnimatePresence>
        
        {/* Scanning Line Effect */}
        <motion.div 
          animate={{ top: ['0%', '100%', '0%'] }}
          transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
          className="absolute left-0 right-0 h-[1px] bg-[#FF3300]/30 z-20 pointer-events-none shadow-[0_0_5px_#FF3300]"
        />
      </div>

      {/* Main Feed */}
      <div className="flex-1 flex flex-col gap-3 overflow-hidden">
        <div 
          ref={scrollRef}
          className="flex-1 bg-black border border-[#222] rounded overflow-y-auto font-mono text-[10px] space-y-2 p-2 scrollbar-hide"
        >
          <AnimatePresence initial={false}>
            {detections.length === 0 && (
              <div className="text-[#333] text-center mt-20 italic">
                "Awaiting Ares visual telemetry..."
              </div>
            )}
            {detections.map((det, i) => (
              <motion.div 
                key={det.timestamp + i}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                onClick={() => setSelectedDetection(det)}
                className={`
                  p-2 rounded border cursor-pointer transition-all
                  ${det.confidence > 0.8 ? 'bg-[#FF3300]/5 border-[#FF3300]/30' : 'bg-[#111] border-[#222]'}
                  hover:border-[#FF3300]/60
                `}
              >
                <div className="flex justify-between items-start mb-1">
                  <div className="flex items-center gap-2">
                    <span className="ares-text font-bold uppercase">{det.object}</span>
                  </div>
                  <span className="text-[#444]">{new Date(det.timestamp).toLocaleTimeString()}</span>
                </div>
                <div className="flex items-center gap-3 text-[#888]">
                  <span className="flex items-center gap-1"><Camera className="w-3 h-3" /> {det.camera}</span>
                  <span className="flex items-center gap-1"><Target className="w-3 h-3" /> {Math.round(det.confidence * 100)}%</span>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-3 gap-2 z-10">
        <div className="bg-black/50 border border-[#222] p-2 rounded text-center">
          <div className="micro-label text-[8px] text-[#444]">Grid Cams</div>
          <div className="text-[12px] font-mono text-[#00FFFF]">3</div>
        </div>
        <div className="bg-black/50 border border-[#222] p-2 rounded text-center">
          <div className="micro-label text-[8px] text-[#444]">Detections</div>
          <div className="text-[12px] font-mono ares-text">{detections.length}</div>
        </div>
        <div className="bg-black/50 border border-[#222] p-2 rounded text-center">
          <div className="micro-label text-[8px] text-[#444]">Threat Level</div>
          <div className="text-[12px] font-mono text-[#FFCC00]">LOW</div>
        </div>
      </div>

      {/* Detail Modal */}
      <AnimatePresence>
        {selectedDetection && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-black/95 z-50 p-4 flex flex-col gap-4"
          >
            <div className="flex justify-between items-center">
              <h3 className="micro-label ares-text">ARES_DETECTION_DETAIL</h3>
              <button onClick={() => setSelectedDetection(null)} className="text-[#888] hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="relative flex-1 bg-black border border-[#FF3300]/30 rounded overflow-hidden">
              <img 
                src={selectedDetection.saved_image} 
                alt="Detection" 
                className="w-full h-full object-contain opacity-80 grayscale contrast-125"
                referrerPolicy="no-referrer"
              />
              <div className="absolute top-2 left-2 bg-black/60 px-2 py-1 rounded border border-[#FF3300]/30 text-[10px] text-[#FF3300] font-mono">
                {selectedDetection.camera} // {selectedDetection.object}
              </div>
              
              {/* Dynamic Bounding Box */}
              <div 
                className="absolute border-2 border-[#FF3300] pointer-events-none animate-pulse"
                style={{
                  left: `${(selectedDetection.bbox[0] / 640) * 100}%`,
                  top: `${(selectedDetection.bbox[1] / 480) * 100}%`,
                  width: `${((selectedDetection.bbox[2] - selectedDetection.bbox[0]) / 640) * 100}%`,
                  height: `${((selectedDetection.bbox[3] - selectedDetection.bbox[1]) / 480) * 100}%`,
                }}
              />
            </div>

            <div className="grid grid-cols-2 gap-4 font-mono text-[10px]">
              <div className="space-y-1">
                <div className="text-[#444]">TIMESTAMP:</div>
                <div className="text-[#eee]">{new Date(selectedDetection.timestamp).toLocaleString()}</div>
                <div className="text-[#444]">CONFIDENCE:</div>
                <div className="text-[#eee]">{selectedDetection.confidence}</div>
              </div>
              <div className="space-y-1">
                <div className="text-[#444]">SIZE:</div>
                <div className="text-[#eee]">{selectedDetection.size}</div>
                <div className="text-[#444]">BBOX:</div>
                <div className="text-[#eee]">{JSON.stringify(selectedDetection.bbox)}</div>
              </div>
            </div>

            <button 
              className="w-full py-2 bg-[#FF3300]/10 border border-[#FF3300]/50 rounded micro-label hover:bg-[#FF3300]/20 transition-all ares-text"
              onClick={() => setSelectedDetection(null)}
            >
              CLOSE_DETAIL
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
