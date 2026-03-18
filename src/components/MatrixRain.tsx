import React, { useEffect, useRef } from 'react';

interface Props {
  color?: string;
  speed?: number;
}

export function MatrixRain({ color = '#00ff66', speed = 33 }: Props) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let drops: number[] = [];
    const fontSize = 14;
    const chars = '01NOVA🐉⚡ABCDEFGHIJKLMNOPQRSTUVWXYZ';

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      const columns = Math.floor(canvas.width / fontSize);
      drops = new Array(columns).fill(1);
    };

    resize();
    window.addEventListener('resize', resize);

    const draw = () => {
      ctx.fillStyle = 'rgba(0,0,0,0.08)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      ctx.fillStyle = color;
      ctx.shadowBlur = 10;
      ctx.shadowColor = color;
      ctx.font = `bold ${fontSize}px monospace`;

      for (let i = 0; i < drops.length; i++) {
        const text = chars[Math.floor(Math.random() * chars.length)];
        ctx.fillText(text, i * fontSize, drops[i] * fontSize);

        if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
          drops[i] = 0;
        }

        drops[i]++;
      }
    };

    const interval = setInterval(draw, speed);

    return () => {
      clearInterval(interval);
      window.removeEventListener('resize', resize);
    };
  }, [color, speed]);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 opacity-20 pointer-events-none z-0"
    />
  );
}
