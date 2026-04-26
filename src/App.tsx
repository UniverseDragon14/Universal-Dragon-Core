import React, { useState, useEffect } from 'react';
import { SpeedInsights } from '@vercel/speed-insights/react';
import { Header } from './components/Header';
import { TelemetryPanel } from './components/TelemetryPanel';
import { SpatialMap } from './components/SpatialMap';
import { Terminal } from './components/Terminal';
import { DragonEye } from './components/DragonEye';
import { RobotControlPanel } from './components/RobotControlPanel';
import { RobotStatusSummary } from './components/RobotStatusSummary';
import { NovaCore } from './components/NovaCore';
import { VoiceAssistant } from './components/VoiceAssistant';
import { AutoCodeEngine } from './components/AutoCodeEngine';
import { WhatsAppBypass } from './components/WhatsAppBypass';
import { SystemLogs } from './components/SystemLogs';
import { QuickActions } from './components/QuickActions';
import { io } from 'socket.io-client';
import { TelemetryData, MapPoint } from './types';
import { MOCK_LOG_MESSAGES, MOCK_SYSTEM_EVENTS, MOCK_SYSTEM_ERRORS } from './constants';

// Mock data generation helpers
const generateCpuData = (length: number): TelemetryData[] => 
  Array.from({ length }, (_, i) => ({
    time: i,
    usage: Math.floor(Math.random() * 40) + 20,
    temp: Math.floor(Math.random() * 15) + 40,
  }));

const generateMapData = (): MapPoint[] => 
  Array.from({ length: 50 }, () => ({
    x: Math.random() * 200 - 100,
    y: Math.random() * 200 - 100,
    z: Math.random() * 100,
  }));

export default function App() {
  const [cpuData, setCpuData] = useState<TelemetryData[]>(generateCpuData(20));
  const [mapData, setMapData] = useState<MapPoint[]>(generateMapData());
  const [logs, setLogs] = useState<string[]>([]);
  const [systemLogs, setSystemLogs] = useState<{ type: 'EVENT' | 'ERROR'; message: string; timestamp: string }[]>([]);
  const [uptime, setUptime] = useState(0);

  useEffect(() => {
    const socket = io();
    socket.on('dragon_eye_detection', (det: any) => {
      const timestamp = new Date().toISOString().split('T')[1].slice(0, -1);
      const newLog = `[DRAGON_EYE] ${timestamp} - DETECTED: ${det.object.toUpperCase()} on ${det.camera} (Conf: ${det.confidence})`;
      setLogs(prev => [...prev.slice(-15), newLog]);
      
      // Add a point to the map
      setMapData(prev => [...prev, {
        x: Math.random() * 200 - 100,
        y: Math.random() * 200 - 100,
        z: Math.random() * 100,
        isDetection: true
      }].slice(-60));
    });

    // Uptime counter
    const uptimeInterval = setInterval(() => {
      setUptime(prev => prev + 1);
    }, 1000);

    // Mock telemetry interval
    const telemetryInterval = setInterval(() => {
      setCpuData(prev => {
        const lastTime = prev.length > 0 ? prev[prev.length - 1].time : 0;
        const newData = [...prev.slice(1), {
          time: lastTime + 1,
          usage: Math.floor(Math.random() * 40) + 20,
          temp: Math.floor(Math.random() * 15) + 40,
        }];
        return newData;
      });
      
      setMapData(generateMapData());
      
      const timestamp = new Date().toISOString().split('T')[1].slice(0, -1);
      const randomMsg = MOCK_LOG_MESSAGES[Math.floor(Math.random() * MOCK_LOG_MESSAGES.length)];
      const prefix = Math.random() > 0.7 ? '[NOVA]' : '[SYS]';
      const newLog = `${prefix} ${timestamp} - ${randomMsg}`;
      setLogs(prev => [...prev.slice(-15), newLog]);

      // Generate System Logs
      if (Math.random() > 0.8) {
        const isError = Math.random() > 0.7;
        const messages = isError ? MOCK_SYSTEM_ERRORS : MOCK_SYSTEM_EVENTS;
        const msg = messages[Math.floor(Math.random() * messages.length)];
        setSystemLogs(prev => [...prev.slice(-10), {
          type: isError ? 'ERROR' : 'EVENT',
          message: msg,
          timestamp: timestamp
        }]);
      }
    }, 1000);

    return () => {
      socket.disconnect();
      clearInterval(uptimeInterval);
      clearInterval(telemetryInterval);
    };
  }, []);

  const formatUptime = (seconds: number) => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  return (
    <div className="min-h-screen p-4 md:p-6 flex flex-col gap-6 relative">
      {/* Tron 3D Grid Background */}
      <div className="tron-grid">
        <div className="tron-grid-inner" />
      </div>

      <Header uptime={formatUptime(uptime)} />
      <QuickActions />

      <main className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Telemetry, Dragon Eye Vision & Auto Code Engine */}
        <div className="lg:col-span-3 flex flex-col gap-6">
          <div className="flex-1">
            <TelemetryPanel data={cpuData} />
          </div>
          <div className="flex-1">
            <DragonEye />
          </div>
          <div className="flex-1">
            <AutoCodeEngine />
          </div>
        </div>

        {/* Middle Column: Spatial Map, Terminal & Voice Assistant */}
        <div className="lg:col-span-6 flex flex-col gap-6">
          <div className="flex-1">
            <SpatialMap data={mapData} />
          </div>
          <div className="flex-1 grid grid-cols-1 md:grid-cols-3 gap-6">
            <Terminal logs={logs} />
            <SystemLogs logs={systemLogs} />
            <VoiceAssistant />
          </div>
        </div>

        {/* Right Column: Status, Control, NovaCore & WhatsApp Bypass */}
        <div className="lg:col-span-3 flex flex-col gap-6">
          <RobotStatusSummary />
          <NovaCore />
          <div className="flex-1">
            <RobotControlPanel />
          </div>
          <div className="flex-1">
            <WhatsAppBypass />
          </div>
        </div>
      </main>

      {/* Footer Decoration */}
      <footer className="flex items-center justify-between px-4 py-2 opacity-20 pointer-events-none">
        <div className="text-[8px] font-mono tracking-[0.2em]">UNIVERSAL_DRAGON_GRID_V7.0_STABLE</div>
        <div className="text-[8px] font-mono tracking-[0.2em]">MASTER_ASLAM_REAL_CREATOR</div>
      </footer>
      <SpeedInsights />
    </div>
  );
}



