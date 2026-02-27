import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { TelemetryPanel } from './components/TelemetryPanel';
import { SpatialMap } from './components/SpatialMap';
import { Terminal } from './components/Terminal';
import { ControlPanel } from './components/ControlPanel';
import { TelemetryData, MapPoint } from './types';
import { MOCK_LOG_MESSAGES } from './constants';

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
  const [uptime, setUptime] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
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
      setUptime(prev => prev + 1);
      
      const timestamp = new Date().toISOString().split('T')[1].slice(0, -1);
      const randomMsg = MOCK_LOG_MESSAGES[Math.floor(Math.random() * MOCK_LOG_MESSAGES.length)];
      const newLog = `[SYS] ${timestamp} - ${randomMsg}`;
      setLogs(prev => [...prev.slice(-8), newLog]);
      
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  const formatUptime = (seconds: number) => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  return (
    <div className="min-h-screen p-4 md:p-6 flex flex-col gap-6">
      <Header uptime={formatUptime(uptime)} />

      <main className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column */}
        <div className="lg:col-span-3">
          <TelemetryPanel data={cpuData} />
        </div>

        {/* Middle Column */}
        <div className="lg:col-span-6 flex flex-col gap-6">
          <SpatialMap data={mapData} />
          <Terminal logs={logs} />
        </div>

        {/* Right Column */}
        <div className="lg:col-span-3">
          <ControlPanel />
        </div>
      </main>
    </div>
  );
}

