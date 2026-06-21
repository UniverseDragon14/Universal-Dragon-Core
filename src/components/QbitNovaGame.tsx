import { useMemo, useState } from 'react';

type Point = { x: number; y: number };
type Qbit = '0' | '1' | 'mix';
type Cell = 'empty' | 'nova' | 'wall' | 'orb' | 'gate' | 'core';

type Level = {
  title: string;
  lesson: string;
  width: number;
  height: number;
  start: Point;
  orb?: Point;
  gate?: Point;
  core: Point;
  walls: Point[];
  needsOne?: boolean;
  starter: string;
};

type State = {
  pos: Point;
  orb: boolean;
  gate: boolean;
  qbit: Qbit;
  observed: '0' | '1' | null;
  steps: number;
  done: boolean;
  note: string;
  log: string[];
};

const LEVELS: Level[] = [
  {
    title: 'Level 1: Wake Nova',
    lesson: 'Learn direct commands: move and activate.',
    width: 3,
    height: 1,
    start: { x: 0, y: 0 },
    core: { x: 2, y: 0 },
    walls: [],
    starter: `# reach the core\nmove right\nmove right\nactivate core`,
  },
  {
    title: 'Level 2: Orb Loop',
    lesson: 'Use repeat so code is smaller and cleaner.',
    width: 5,
    height: 1,
    start: { x: 0, y: 0 },
    orb: { x: 3, y: 0 },
    gate: { x: 4, y: 0 },
    core: { x: 4, y: 0 },
    walls: [],
    starter: `# repeat removes copy paste\nrepeat 3 {\n  move right\n}\ncollect orb\nactivate gate\nmove right\nactivate core`,
  },
  {
    title: 'Level 3: Qbit Gate',
    lesson: 'Use h, measure, and if nova == 1.',
    width: 5,
    height: 3,
    start: { x: 0, y: 0 },
    orb: { x: 4, y: 0 },
    gate: { x: 4, y: 1 },
    core: { x: 4, y: 2 },
    walls: [
      { x: 1, y: 1 },
      { x: 2, y: 1 },
      { x: 3, y: 1 },
    ],
    needsOne: true,
    starter: `# qbit decides the final step\nrepeat 4 {\n  move right\n}\ncollect orb\nactivate gate\nmove down\nh nova\nprob nova\nmeasure nova\nif nova == 1: move down\nactivate core`,
  },
];

const LOOK: Record<Cell, string> = {
  empty: 'border-white/10 bg-black/40 text-white/30',
  nova: 'border-cyan-300/80 bg-cyan-400/20 text-cyan-100 shadow-[0_0_20px_rgba(0,255,255,0.25)]',
  wall: 'border-red-500/60 bg-red-950/50 text-red-200',
  orb: 'border-yellow-300/70 bg-yellow-400/20 text-yellow-100',
  gate: 'border-orange-500/70 bg-orange-950/50 text-orange-100',
  core: 'border-fuchsia-300/70 bg-fuchsia-500/20 text-fuchsia-100 shadow-[0_0_20px_rgba(217,70,239,0.25)]',
};

const LABEL: Record<Cell, string> = { empty: '·', nova: 'N', wall: '█', orb: 'ORB', gate: 'GATE', core: 'CORE' };
const same = (a: Point | undefined, b: Point) => Boolean(a && a.x === b.x && a.y === b.y);
const key = (p: Point) => `${p.x},${p.y}`;
const near = (a: Point, b: Point) => Math.abs(a.x - b.x) + Math.abs(a.y - b.y) <= 1;
const fresh = (level: Level): State => ({ pos: { ...level.start }, orb: false, gate: false, qbit: '0', observed: null, steps: 0, done: false, note: 'Ready. Edit commands and start.', log: ['QBIT NOVA ONLINE', 'Creator: Aslam / Universal Dragon'] });
const probs = (q: Qbit) => (q === 'mix' ? { p0: 0.5, p1: 0.5 } : q === '1' ? { p0: 0, p1: 1 } : { p0: 1, p1: 0 });

function expand(source: string) {
  const lines = source.split('\n').map((x) => x.trim()).filter((x) => x && !x.startsWith('#'));
  const walk = (i: number): { out: string[]; next: number } => {
    const out: string[] = [];
    for (; i < lines.length; i += 1) {
      const line = lines[i];
      if (line === '}') return { out, next: i + 1 };
      const rep = line.match(/^repeat\s+(\d+)\s*\{$/i);
      if (rep) {
        const child = walk(i + 1);
        for (let n = 0; n < Math.min(Number(rep[1]), 20); n += 1) out.push(...child.out);
        i = child.next - 1;
      } else out.push(line.replace(/;$/, ''));
    }
    return { out, next: lines.length };
  };
  return walk(0).out.slice(0, 80);
}

function check(cond: string, state: State) {
  const text = cond.trim().toLowerCase();
  if (text === 'orb == true') return state.orb;
  if (text === 'gate == true') return state.gate;
  const nova = text.match(/^nova\s*==\s*([01])$/);
  return nova ? state.observed === nova[1] : false;
}

function step(cmd: string, state: State, level: Level, log: string[]): State {
  let s: State = { ...state, pos: { ...state.pos } };
  const lower = cmd.toLowerCase();
  const ask = cmd.match(/^if\s+(.+?)\s*:\s*(.+)$/i);
  if (ask) {
    if (check(ask[1], s)) {
      log.push(`IF true: ${ask[1]}`);
      return step(ask[2], s, level, log);
    }
    log.push(`IF false: ${ask[1]}`);
    return s;
  }
  const move = lower.match(/^move\s+(up|down|left|right)$/);
  if (move) {
    const d: Record<string, Point> = { up: { x: 0, y: -1 }, down: { x: 0, y: 1 }, left: { x: -1, y: 0 }, right: { x: 1, y: 0 } };
    const next = { x: s.pos.x + d[move[1]].x, y: s.pos.y + d[move[1]].y };
    const walls = new Set(level.walls.map(key));
    if (next.x < 0 || next.y < 0 || next.x >= level.width || next.y >= level.height || walls.has(key(next))) {
      log.push(`STOP at ${key(next)}`);
      s.note = 'Path stopped. Fix the command order.';
      return s;
    }
    if (same(level.gate, next) && !s.gate) {
      log.push('GATE needs orb first');
      s.note = 'Gate is inactive.';
      return s;
    }
    s.pos = next;
    s.steps += 1;
    log.push(`MOVE ${move[1]} => ${key(next)}`);
    return s;
  }
  if (lower === 'collect orb') {
    if (same(level.orb, s.pos)) {
      s.orb = true;
      log.push('ORB collected');
    } else log.push('No orb here');
    return s;
  }
  if (lower === 'activate gate') {
    if (!level.gate) log.push('No gate in this level');
    else if (s.orb && near(s.pos, level.gate)) {
      s.gate = true;
      log.push('GATE active');
    } else log.push('Gate needs orb and near position');
    return s;
  }
  if (lower === 'h nova') {
    s.qbit = 'mix';
    s.observed = null;
    log.push('H nova => P0 0.5 / P1 0.5');
    return s;
  }
  if (lower === 'x nova') {
    s.qbit = s.qbit === '0' ? '1' : s.qbit === '1' ? '0' : 'mix';
    s.observed = null;
    log.push(`X nova => ${s.qbit}`);
    return s;
  }
  if (lower === 'prob nova') {
    const p = probs(s.qbit);
    log.push(`PROB nova => P0 ${p.p0.toFixed(1)} / P1 ${p.p1.toFixed(1)}`);
    return s;
  }
  if (lower === 'measure nova') {
    const result = s.qbit === 'mix' ? (Math.random() < 0.5 ? '0' : '1') : s.qbit;
    s.qbit = result;
    s.observed = result;
    log.push(`MEASURE nova => ${result}`);
    return s;
  }
  if (lower === 'activate core') {
    if (!same(s.pos, level.core)) log.push(`CORE waits at ${key(level.core)}`);
    else if (level.needsOne && s.observed !== '1') log.push('CORE needs nova == 1');
    else {
      s.done = true;
      s.note = 'Dragon Core complete. Lesson passed.';
      log.push('MISSION COMPLETE');
    }
    return s;
  }
  log.push(`Unknown: ${cmd}`);
  return s;
}

export function QbitNovaGame() {
  const [levelIndex, setLevelIndex] = useState(0);
  const level = LEVELS[levelIndex];
  const [code, setCode] = useState(level.starter);
  const [state, setState] = useState<State>(() => fresh(level));
  const wallSet = useMemo(() => new Set(level.walls.map(key)), [level]);
  const p = probs(state.qbit);

  const reset = (i = levelIndex) => {
    setLevelIndex(i);
    setCode(LEVELS[i].starter);
    setState(fresh(LEVELS[i]));
  };

  const start = () => {
    const commands = expand(code);
    const log = [`START ${commands.length} command(s)`];
    let next = { ...state, done: false, note: 'Mission ran.' };
    for (const cmd of commands) {
      next = step(cmd, next, level, log);
      if (next.done) break;
    }
    setState({ ...next, log: [...log, ...next.log].slice(0, 70) });
  };

  const kind = (point: Point): Cell => same(state.pos, point) ? 'nova' : wallSet.has(key(point)) ? 'wall' : same(level.orb, point) && !state.orb ? 'orb' : same(level.gate, point) && !state.gate ? 'gate' : same(level.core, point) ? 'core' : 'empty';

  return (
    <section className="glass-panel p-4 md:p-5 flex flex-col gap-4 min-h-[420px]">
      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div>
          <div className="micro-label">QBIT NOVA GAME / PROGRAMMING LAB</div>
          <h2 className="text-xl md:text-2xl font-bold tracking-tight"><span className="neon-text">Qbit Nova</span> <span className="ares-text">Dragon Core</span></h2>
          <p className="text-sm text-white/60 max-w-2xl">{level.lesson}</p>
        </div>
        <div className="flex flex-wrap gap-2 text-xs font-mono">
          <span className="px-2 py-1 border border-cyan-400/40 bg-cyan-400/10 text-cyan-100">Creator: Aslam</span>
          <span className="px-2 py-1 border border-red-400/40 bg-red-400/10 text-red-100">Universal Dragon</span>
          <span className="px-2 py-1 border border-white/10 bg-white/5 text-white/70">{level.title}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-4">
        <div className="xl:col-span-5 flex flex-col gap-3">
          <div className="flex items-center justify-between"><div className="micro-label">Mission Grid</div><div className="text-xs font-mono text-white/50">pos {key(state.pos)} / steps {state.steps}</div></div>
          <div className="grid gap-2 rounded border border-white/10 bg-black/40 p-3" style={{ gridTemplateColumns: `repeat(${level.width}, minmax(44px, 1fr))` }}>
            {Array.from({ length: level.width * level.height }, (_, index) => {
              const point = { x: index % level.width, y: Math.floor(index / level.width) };
              const cell = kind(point);
              return <div key={key(point)} className={`aspect-square min-h-12 rounded border flex items-center justify-center text-[10px] md:text-xs font-mono font-bold ${LOOK[cell]}`}>{LABEL[cell]}</div>;
            })}
          </div>
          <div className="grid grid-cols-3 gap-2 text-xs font-mono"><div className="border border-white/10 bg-white/5 p-2 rounded">ORB: {state.orb ? 'YES' : 'NO'}</div><div className="border border-white/10 bg-white/5 p-2 rounded">GATE: {state.gate ? 'ON' : 'OFF'}</div><div className="border border-white/10 bg-white/5 p-2 rounded">NOVA: {state.observed ?? state.qbit}</div></div>
          <div className="rounded border border-cyan-400/20 bg-cyan-400/5 p-3"><div className="flex items-center justify-between text-xs font-mono text-white/60 mb-2"><span>QBIT probability</span><span>P0 {p.p0.toFixed(1)} / P1 {p.p1.toFixed(1)}</span></div><div className="h-3 rounded bg-white/10 overflow-hidden flex"><div className="bg-cyan-400/70" style={{ width: `${p.p0 * 100}%` }} /><div className="bg-red-500/70" style={{ width: `${p.p1 * 100}%` }} /></div></div>
        </div>

        <div className="xl:col-span-4 flex flex-col gap-3">
          <div className="flex items-center justify-between"><div className="micro-label">NovaScript Editor</div><button type="button" onClick={() => setCode(level.starter)} className="text-xs font-mono px-2 py-1 border border-white/10 bg-white/5 hover:bg-white/10 rounded">LOAD STARTER</button></div>
          <textarea value={code} onChange={(event) => setCode(event.target.value)} spellCheck={false} className="min-h-[260px] flex-1 resize-y rounded border border-cyan-400/20 bg-black/70 p-3 font-mono text-xs md:text-sm text-cyan-50 outline-none focus:border-cyan-300/70" />
          <div className="flex flex-wrap gap-2"><button type="button" onClick={start} className="px-3 py-2 rounded border border-cyan-300/50 bg-cyan-400/10 hover:bg-cyan-400/20 text-cyan-50 text-xs font-mono font-bold">START</button><button type="button" onClick={() => reset()} className="px-3 py-2 rounded border border-white/10 bg-white/5 hover:bg-white/10 text-white/80 text-xs font-mono">RESET</button><button type="button" onClick={() => reset((levelIndex + 1) % LEVELS.length)} className="px-3 py-2 rounded border border-red-400/50 bg-red-500/10 hover:bg-red-500/20 text-red-100 text-xs font-mono">NEXT LEVEL</button></div>
        </div>

        <div className="xl:col-span-3 flex flex-col gap-3">
          <div><div className="micro-label">Runtime Message</div><div className={`mt-2 rounded border p-3 text-sm font-mono ${state.done ? 'border-emerald-300/50 bg-emerald-500/10 text-emerald-100' : 'border-white/10 bg-white/5 text-white/70'}`}>{state.note}</div></div>
          <div className="flex-1 min-h-[260px] rounded border border-white/10 bg-black/60 p-3 overflow-auto"><div className="micro-label mb-2">Execution Log</div><div className="space-y-1 font-mono text-[11px] text-white/65">{state.log.map((entry, index) => <div key={`${entry}-${index}`} className="border-b border-white/5 pb-1">{entry}</div>)}</div></div>
          <div className="rounded border border-red-400/20 bg-red-500/5 p-3 text-xs text-white/60 leading-relaxed">Commands: <span className="font-mono text-cyan-100">move right</span>, <span className="font-mono text-cyan-100">repeat 3</span>, <span className="font-mono text-cyan-100">collect orb</span>, <span className="font-mono text-cyan-100">h nova</span>, <span className="font-mono text-cyan-100">measure nova</span>, <span className="font-mono text-cyan-100">if nova == 1: move down</span>.</div>
        </div>
      </div>
    </section>
  );
}
