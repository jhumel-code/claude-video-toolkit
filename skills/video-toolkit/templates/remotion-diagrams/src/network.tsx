// network.tsx — stateful network-diagram primitives (v3): curved flow edges with
// travelling particles, ring/app nodes that flip state mid-scene (live → down),
// stat cards, tag pills, and a timed bottom caption. Unlike the Section/spec model
// (reveal-only), these components read a `states` timeline: seconds measured from
// the start of the enclosing Sequence.
import React from 'react';
import { useCurrentFrame } from 'remotion';
import { BRAND, FPS } from './brand';

const px = (n: number) => `${n}px`;
export const rgba = (hex: string, a: number) => {
  const n = parseInt(hex.slice(1), 16);
  return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a})`;
};

type St<T extends string> = { at: number; s: T };

// last state at or before `sec`, the state before it, and seconds since the switch —
// enough to ease any visual from prev → current without per-component bookkeeping.
export function stateAt<T extends string>(states: St<T>[] | undefined, init: T, sec: number): { s: T; prev: T; since: number } {
  const ss = [...(states ?? [])].sort((a, b) => a.at - b.at);
  let s: T = init, prev: T = init, since = 1e9;
  for (const st of ss) if (st.at <= sec) { prev = s; s = st.s; since = sec - st.at; }
  return { s, prev, since };
}

// ---- svg layer the flow edges live in (explicit size: works in any composition) ----
export const EdgeLayer: React.FC<{ w: number; h: number; children: React.ReactNode }> = ({ w, h, children }) => (
  <svg width={w} height={h} style={{ position: 'absolute', left: 0, top: 0 }}>{children}</svg>
);

// ---- curved edge with particles riding it; states: 'flow' (particles) / 'dead' (faint) ----
export const FlowEdge: React.FC<{
  x1: number; y1: number; x2: number; y2: number;
  states?: St<'flow' | 'dead'>[]; init?: 'flow' | 'dead';
  color?: string; particles?: number; speed?: number; seed?: number; bend?: number; size?: number;
}> = ({ x1, y1, x2, y2, states, init = 'flow', color = BRAND.link, particles = 3, speed = 0.4, seed = 0, bend = 0.5, size = 1 }) => {
  const sec = useCurrentFrame() / FPS;
  const st = stateAt(states, init, sec);
  const to = st.s === 'flow' ? 1 : 0;
  const from = st.prev === 'flow' ? 1 : 0;
  const flow = from + (to - from) * Math.min(1, st.since / 0.35);
  // horizontal-S cubic (node-editor style): tangents leave/enter horizontally
  const dx = x2 - x1;
  const c1 = { x: x1 + dx * bend, y: y1 }, c2 = { x: x2 - dx * bend, y: y2 };
  const P = (t: number) => { const u = 1 - t; return {
    x: u * u * u * x1 + 3 * u * u * t * c1.x + 3 * u * t * t * c2.x + t * t * t * x2,
    y: u * u * u * y1 + 3 * u * u * t * c1.y + 3 * u * t * t * c2.y + t * t * t * y2 }; };
  const d = `M ${x1} ${y1} C ${c1.x} ${c1.y}, ${c2.x} ${c2.y}, ${x2} ${y2}`;
  const dots = Array.from({ length: particles }, (_, i) => {
    const t = ((sec * speed + i / particles + seed * 0.377) % 1 + 1) % 1;
    return { ...P(t), o: Math.sin(Math.PI * t) }; // ease in/out of the endpoints
  });
  return (
    <>
      {/* The rail must read in BOTH states: a dead edge is a visible line that
          carries nothing (the "no write path" story depends on seeing it), and
          a flowing edge should not rely on its particles alone to be seen. */}
      <path d={d} fill="none" stroke={BRAND.ink} strokeWidth={2 * size} opacity={0.16 + 0.16 * flow} />
      <path d={d} fill="none" stroke={color} strokeWidth={1.5 * size} opacity={0.12 + 0.28 * flow} strokeDasharray={`${size} ${7 * size}`} strokeLinecap="round" />
      {flow > 0.02 && dots.map((p, i) => (
        <g key={i} opacity={flow * p.o}>
          <circle cx={p.x} cy={p.y} r={7 * size} fill={color} opacity={0.28} />
          <circle cx={p.x} cy={p.y} r={3 * size} fill="#EAF6FF" />
        </g>
      ))}
    </>
  );
};

// ---- ring node (hub/edge/router): circled icon, label above, status below; live → down ----
export const RingNode: React.FC<{
  x: number; y: number; r?: number;
  labelTop?: string; labelTopColor?: string;
  subLive?: string; subDown?: string; subColor?: string;
  states?: St<'live' | 'down'>[]; init?: 'live' | 'down'; liveColor?: string;
}> = ({ x, y, r = 50, labelTop, labelTopColor, subLive, subDown = 'OFFLINE', subColor, states, init = 'live', liveColor = BRAND.link }) => {
  const sec = useCurrentFrame() / FPS;
  const st = stateAt(states, init, sec);
  const down = st.s === 'down';
  const col = down ? BRAND.danger : liveColor;
  const switching = st.since < 0.35 && st.prev !== st.s;
  const k = switching ? 1 + 0.16 * (1 - st.since / 0.35) : 1;
  const pulse = down ? 0.20 : 0.10 + 0.07 * Math.sin(sec * Math.PI * 1.5 + x);
  const sub = down ? subDown : subLive;
  const bar: React.CSSProperties = { width: r * 0.72, height: 3.5, borderRadius: 2, background: col };
  return (
    <>
      <div style={{ position: 'absolute', left: px(x - r), top: px(y - r), width: px(2 * r), height: px(2 * r), transform: `scale(${k})` }}>
        <div style={{ position: 'absolute', inset: -11, borderRadius: 999, border: `1px solid ${col}`, opacity: pulse }} />
        <div style={{
          position: 'absolute', inset: 0, borderRadius: 999, border: `2.5px solid ${col}`,
          background: rgba(col, 0.10), boxShadow: `0 0 30px ${rgba(col, down ? 0.35 : 0.20)}`,
          display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 5,
        }}>
          {down
            ? <div style={{ position: 'relative', width: r * 0.72, height: r * 0.72 }}>
                {[45, -45].map((a) => <div key={a} style={{ position: 'absolute', left: 0, top: '50%', width: '100%', height: 3.5, borderRadius: 2, background: col, transform: `rotate(${a}deg)` }} />)}
              </div>
            : <><div style={bar} /><div style={bar} /><div style={bar} /></>}
        </div>
      </div>
      {labelTop && <div style={{ position: 'absolute', left: px(x - 200), top: px(y - r - 44), width: 400, textAlign: 'center', fontFamily: 'GeistMono', fontSize: 17, fontWeight: 700, letterSpacing: '0.14em', color: labelTopColor ?? col }}>{labelTop}</div>}
      {sub && <div style={{ position: 'absolute', left: px(x - 200), top: px(y + r + 16), width: 400, textAlign: 'center', fontFamily: 'GeistMono', fontSize: 15, letterSpacing: '0.08em', color: down ? BRAND.danger : (subColor ?? BRAND.soft) }}>{sub}</div>}
    </>
  );
};

// ---- app node: monogram circle + name + LIVE/OFFLINE tag (no third-party logos) ----
export const AppNode: React.FC<{
  x: number; y: number; name: string;
  states?: St<'live' | 'down'>[]; init?: 'live' | 'down';
}> = ({ x, y, name, states, init = 'live' }) => {
  const sec = useCurrentFrame() / FPS;
  const st = stateAt(states, init, sec);
  const down = st.s === 'down';
  const to = down ? 0.38 : 1, from = st.prev === 'down' ? 0.38 : 1;
  const a = from + (to - from) * Math.min(1, st.since / 0.35);
  return (
    <div style={{ position: 'absolute', left: px(x - 27), top: px(y - 27), opacity: a, display: 'flex', alignItems: 'center', gap: 16 }}>
      <div style={{
        width: 54, height: 54, borderRadius: 999, background: BRAND.panel, border: `1px solid ${rgba(BRAND.ink, 0.25)}`,
        display: 'flex', alignItems: 'center', justifyContent: 'center', flex: 'none',
        fontFamily: 'Geist', fontWeight: 600, fontSize: 24, color: BRAND.ink,
      }}>{name[0]}</div>
      <div>
        <div style={{ fontFamily: 'Geist', fontWeight: 600, fontSize: 26, color: BRAND.ink, lineHeight: 1.1 }}>{name}</div>
        <div style={{ fontFamily: 'GeistMono', fontSize: 12, letterSpacing: '0.22em', marginTop: 4, color: down ? BRAND.soft : BRAND.good }}>{down ? 'OFFLINE' : 'LIVE'}</div>
      </div>
    </div>
  );
};

// ---- source card: rounded rect with a queue-dots spine (the "traffic" box) ----
export const SourceCard: React.FC<{ x: number; y: number; w?: number; h?: number; title: string; sub?: string; fs?: number }> =
({ x, y, w = 200, h = 92, title, sub, fs = 24 }) => (
  <div style={{
    position: 'absolute', left: px(x - w / 2), top: px(y - h / 2), width: px(w), height: px(h),
    borderRadius: 14, background: BRAND.panel, border: `1px solid ${rgba(BRAND.ink, 0.18)}`, boxShadow: BRAND.shadow,
    display: 'flex', alignItems: 'center', gap: 16, padding: '0 20px', boxSizing: 'border-box',
  }}>
    <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
      {[0, 1, 2].map((i) => <div key={i} style={{ width: 5, height: 5, borderRadius: 999, background: BRAND.link }} />)}
    </div>
    <div>
      <div style={{ fontFamily: 'Geist', fontWeight: 700, fontSize: fs, letterSpacing: '0.04em', color: BRAND.ink }}>{title}</div>
      {sub && <div style={{ fontFamily: 'GeistMono', fontSize: Math.round(fs * 0.58), color: BRAND.soft, marginTop: 3 }}>{sub}</div>}
    </div>
  </div>
);

// ---- stat card: eyebrow + value, corner-tick framing ----
export const StatCard: React.FC<{ x: number; y: number; w?: number; h?: number; label: string; value: string; color?: string; fs?: number }> =
({ x, y, w = 300, h = 104, label, value, color = BRAND.accent, fs = 33 }) => {
  const tick: React.CSSProperties = { position: 'absolute', width: 12, height: 12, borderColor: color, borderStyle: 'solid' };
  return (
    <div style={{
      position: 'absolute', left: px(x - w / 2), top: px(y - h / 2), width: px(w), height: px(h),
      background: BRAND.panel, border: `1px solid ${rgba(color, 0.40)}`, boxSizing: 'border-box', padding: '16px 22px',
    }}>
      <div style={{ ...tick, left: -1, top: -1, borderWidth: '2px 0 0 2px' }} />
      <div style={{ ...tick, right: -1, bottom: -1, borderWidth: '0 2px 2px 0' }} />
      <div style={{ fontFamily: 'GeistMono', fontSize: Math.round(fs * 0.42), letterSpacing: '0.18em', color }}>{'▪'} {label}</div>
      <div style={{ fontFamily: 'Geist', fontWeight: 600, fontSize: fs, color: BRAND.ink, marginTop: 8 }}>{value}</div>
    </div>
  );
};

// ---- tag pill: bold colored tag + muted description ----
export const TagPill: React.FC<{ x: number; y: number; label: string; text?: string; color?: string }> =
({ x, y, label, text, color = BRAND.accent }) => (
  <div style={{
    position: 'absolute', left: px(x), top: px(y), transform: 'translate(-50%,-50%)',
    display: 'inline-flex', alignItems: 'center', gap: 14, padding: '12px 26px', borderRadius: 999,
    border: `1px solid ${rgba(color, 0.55)}`, background: BRAND.panel, whiteSpace: 'nowrap', boxShadow: BRAND.shadow,
  }}>
    <span style={{ fontFamily: 'GeistMono', fontWeight: 700, fontSize: 19, letterSpacing: '0.06em', color }}>{label}</span>
    {text && <span style={{ fontFamily: 'GeistMono', fontSize: 17, color: BRAND.sub }}>{text}</span>}
  </div>
);

// ---- bottom caption pill: swaps text on a timeline (subtitle-style beats) ----
export const CaptionPill: React.FC<{ x: number; y: number; items: { at: number; t: string }[] }> = ({ x, y, items }) => {
  const sec = useCurrentFrame() / FPS;
  let cur: { at: number; t: string } | null = null;
  for (const it of [...items].sort((a, b) => a.at - b.at)) if (it.at <= sec) cur = it;
  if (!cur) return null;
  const p = Math.min(1, (sec - cur.at) / 0.25);
  return (
    <div style={{
      position: 'absolute', left: px(x), top: px(y), transform: `translate(-50%,-50%) translateY(${(1 - p) * 10}px)`, opacity: p,
      padding: '15px 30px', borderRadius: 999, background: 'rgba(10,22,38,0.92)', border: `1px solid ${rgba(BRAND.ink, 0.14)}`,
      fontFamily: 'Geist', fontWeight: 500, fontSize: 25, color: BRAND.ink, whiteSpace: 'nowrap', boxShadow: BRAND.shadow,
    }}>{cur.t}</div>
  );
};

// ---- vertical header: centered eyebrow + two-tone serif title + mono subtitle ----
export const VHeader: React.FC<{ cx: number; topY?: number; eyebrow?: string; parts: { t: string; c?: string }[]; sub?: string; subColor?: string }> =
({ cx, topY = 96, eyebrow, parts, sub, subColor = BRAND.link }) => (
  <>
    {eyebrow && <div style={{ position: 'absolute', left: px(cx - 400), top: px(topY), width: 800, textAlign: 'center', fontFamily: 'GeistMono', fontSize: 16, letterSpacing: '0.26em', textTransform: 'uppercase', color: BRAND.soft }}>{eyebrow}</div>}
    <div style={{ position: 'absolute', left: px(cx - 500), top: px(topY + 34), width: 1000, textAlign: 'center', fontFamily: 'InstrumentSerif', fontSize: 66, lineHeight: 1.05, color: BRAND.ink, transform: 'scaleX(1.1)', transformOrigin: 'center' }}>
      {parts.map((s, i) => <span key={i} style={{ color: s.c ?? BRAND.ink }}>{s.t}</span>)}
    </div>
    {sub && <div style={{ position: 'absolute', left: px(cx - 450), top: px(topY + 118), width: 900, textAlign: 'center', fontFamily: 'GeistMono', fontSize: 19, letterSpacing: '0.04em', color: subColor }}>{sub}</div>}
  </>
);
