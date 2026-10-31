export interface TelemetryData {
  time: number;
  usage: number;
  temp: number;
}

export interface MapPoint {
  x: number;
  y: number;
  z: number;
  isDetection?: boolean;
}
