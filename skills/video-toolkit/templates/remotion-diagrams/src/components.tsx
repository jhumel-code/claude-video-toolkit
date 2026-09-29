import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate, Easing, Img, staticFile } from 'remotion';
import { BRAND, LIGHT_SKIN, W, H, K } from './brand';

// ---- background: warm white-smoke paper + faint dot grid (diagram-design light, flat = no banding) ----
export const Bg: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: BRAND.paper }}>
    <AbsoluteFill style={{
      backgroundImage: `radial-gradient(${BRAND.dot} 1.5px, transparent 1.6px)`,
      backgroundSize: '34px 34px',
    }} />
  </AbsoluteFill>
);

// ---- eased reveal: fade + slide-up (ease-out cubic) at frame `at` ----
export const Reveal: React.FC<{ at: number; dur?: number; dy?: number; children: React.ReactNode }> =
({ at, dur = 16, dy = 26, children }) => {
  const f = useCurrentFrame();
  const p = interpolate(f, [at, at + K(dur)], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic) });
  return <div style={{ position: 'absolute', inset: 0, opacity: p, transform: `translateY(${(1 - p) * dy}px)` }}>{children}</div>;
};

const px = (n: number) => `${n}px`;

// ---- Microsoft 4-square mark, sizable (no PNG ships for it) ----
const MsGrid: React.FC<{ cell?: number }> = ({ cell = 26 }) => (
  <div style={{ display: 'grid', gridTemplateColumns: `${cell}px ${cell}px`, gridTemplateRows: `${cell}px ${cell}px`, gap: Math.max(3, Math.round(cell * 0.15)) }}>
    {['#F25022', '#7FBA00', '#00A4EF', '#FFB900'].map((c) => <div key={c} style={{ background: c }} />)}
  </div>
);

// ---- node: backend = white + hairline + soft shadow; focal = accent-tint + accent border ----
export const Node: React.FC<{
  x: number; y: number; w: number; h: number; title: string; sub?: string;
  focal?: boolean; logo?: string; cornerLogo?: string; small?: boolean; tcolor?: string;
}> = ({ x, y, w, h, title, sub, focal, logo, cornerLogo, small, tcolor }) => {
  const rad = (w >= 360 || h >= 200) ? 8 : 6;
  return (
    <div style={{
      position: 'absolute', left: px(x - w / 2), top: px(y - h / 2), width: px(w), height: px(h),
      borderRadius: rad, background: focal ? BRAND.panelTint : BRAND.panel,
      border: `${focal ? 1.4 : 1}px solid ${focal ? BRAND.accent : BRAND.line}`,
      boxShadow: BRAND.shadow,
      display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: small ? 7 : 9,
      textAlign: 'center', padding: '0 18px', boxSizing: 'border-box',
    }}>
      {cornerLogo && (cornerLogo === 'ms'
        ? <div style={{ position: 'absolute', left: 18, top: 16 }}><MsGrid cell={16} /></div>
        : cornerLogo === 'trustabl'
        ? <Img src={staticFile('logos/trustabl.png')} style={{ position: 'absolute', left: 20, top: 16, height: 40, objectFit: 'contain' }} />
        : <div style={{ position: 'absolute', left: 20, top: 16, height: 40, padding: LIGHT_SKIN ? 0 : '4px 9px', background: BRAND.logoChip, borderRadius: 6, display: 'flex', alignItems: 'center' }}>
            <Img src={staticFile('logos/' + cornerLogo + '.png')} style={{ height: LIGHT_SKIN ? 40 : 28, objectFit: 'contain' }} />
          </div>)}
      {logo && (logo === 'ms'
        ? <div style={{ marginBottom: 2 }}><MsGrid cell={Math.round(h * 0.145)} /></div>
        : logo === 'trustabl'
        ? <Img src={staticFile('logos/trustabl.png')} style={{ height: px(h * 0.34), marginBottom: 2, objectFit: 'contain' }} />
        : <div style={{ height: px(h * 0.34), marginBottom: 2, padding: LIGHT_SKIN ? 0 : '5px 12px', background: BRAND.logoChip, borderRadius: 7, display: 'flex', alignItems: 'center' }}>
            <Img src={staticFile('logos/' + logo + '.png')} style={{ height: LIGHT_SKIN ? '100%' : '74%', objectFit: 'contain' }} />
          </div>)}
      <div style={{ fontFamily: 'Geist', fontWeight: 600, fontSize: px(small ? 25 : 31), color: tcolor || (focal ? BRAND.accentHi : BRAND.ink), lineHeight: 1.15 }}>{title}</div>
      {sub && <div style={{ width: small ? 30 : 42, height: 1, background: focal ? 'rgba(22,136,122,0.40)' : BRAND.line }} />}
      {sub && <div style={{ fontFamily: 'GeistMono', fontSize: px(17), color: BRAND.soft, letterSpacing: '0.03em', lineHeight: 1.2 }}>{sub}</div>}
    </div>
  );
};

// ---- pill ----
export const Pill: React.FC<{ x: number; y: number; text: string; color?: string; logo?: string; bare?: boolean }> = ({ x, y, text, color, logo, bare }) => (
  <div style={{
    position: 'absolute', left: px(x), top: px(y), transform: 'translate(-50%,-50%)',
    display: 'inline-flex', alignItems: 'center', gap: 12,
    padding: bare ? 0 : (logo ? '11px 26px 11px 20px' : '13px 28px'), borderRadius: 999,
    border: bare ? 'none' : `1px solid ${(color || BRAND.accent)}`,
    background: bare ? 'transparent' : BRAND.panel, color: color ? BRAND.sub : BRAND.accentHi, fontFamily: 'GeistMono', fontSize: px(19), whiteSpace: 'nowrap',
    boxShadow: bare ? 'none' : BRAND.shadow,
  }}>
    {logo && <Img src={staticFile('logos/' + logo + '.png')} style={{ height: 28, objectFit: 'contain' }} />}
    <span>{text}</span>
  </div>
);

// ---- arrows (SVG); head=false draws a plain connector (branch trunk / spine) ----
export const Arrow: React.FC<{ x1: number; y1: number; x2: number; y2: number; label?: string; head?: boolean; dashed?: boolean }> = ({ x1, y1, x2, y2, label, head = true, dashed }) => {
  const ang = Math.atan2(y2 - y1, x2 - x1); const ah = 13;
  const mx = (x1 + x2) / 2, my = (y1 + y2) / 2;
  return (
    <>
      <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={BRAND.accent} strokeWidth={2.4} opacity={0.9} strokeDasharray={dashed ? '9 8' : undefined} />
      {head && <polygon points={`${x2},${y2} ${x2 - ah * Math.cos(ang - 0.5)},${y2 - ah * Math.sin(ang - 0.5)} ${x2 - ah * Math.cos(ang + 0.5)},${y2 - ah * Math.sin(ang + 0.5)}`} fill={BRAND.accent} />}
      {label && <text x={mx} y={my - 15} fill={BRAND.sub} fontFamily="GeistMono" fontSize={17} letterSpacing={1} textAnchor="middle">{label.toUpperCase()}</text>}
    </>
  );
};
export const ArrowSvg: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <svg width={W} height={H} style={{ position: 'absolute', left: 0, top: 0 }}>{children}</svg>
);

// ---- mono "code" card (light: near-white panel + ink text + window dots) ----
export const MonoCard: React.FC<{ x: number; y: number; w: number; h: number; title?: string; lines: { t: string; hi?: boolean; bad?: boolean }[] }> =
({ x, y, w, h, title, lines }) => (
  <div style={{
    position: 'absolute', left: px(x - w / 2), top: px(y - h / 2), width: px(w), height: px(h),
    borderRadius: 12, background: BRAND.mono, border: `1px solid ${BRAND.line}`, boxShadow: BRAND.shadow, boxSizing: 'border-box', overflow: 'hidden',
  }}>
    <div style={{ display: 'flex', gap: 8, padding: '16px 18px 0', alignItems: 'center', borderBottom: `1px solid ${BRAND.line}`, paddingBottom: 12 }}>
      {['#ff5f56', '#ffbd2e', '#27c93f'].map((c) => <div key={c} style={{ width: 11, height: 11, borderRadius: 999, background: c }} />)}
      {title && <div style={{ marginLeft: 'auto', fontFamily: 'GeistMono', fontSize: 16, color: BRAND.soft }}>{title}</div>}
    </div>
    <div style={{ padding: '18px 26px', fontFamily: 'GeistMono', fontSize: 20, lineHeight: 1.5 }}>
      {lines.map((l, i) => (
        <div key={i} style={{ color: l.bad ? BRAND.danger : l.hi ? BRAND.accentHi : BRAND.ink, whiteSpace: 'pre' }}>{l.t}</div>
      ))}
    </div>
  </div>
);

// ---- header: eyebrow (tracked mono) + Instrument Serif title + hairline rule + logo+wordmark/badge ----
const LOGO_NAMES: Record<string, string> = {
  trustabl: 'Trustabl', opa: 'Open Policy Agent', nvidia: 'NVIDIA', owasp: 'OWASP', intoto: 'in-toto',
};

export const Header: React.FC<{ eyebrow?: string; title?: string; titleParts?: { t: string; c?: string }[]; sub?: string; subColor?: string; logo?: string; badge?: string; badgeColor?: string; ms?: boolean }> =
({ eyebrow, title, titleParts, sub, subColor, logo, badge, badgeColor = BRAND.gold, ms }) => (
  <>
    {eyebrow && <div style={{ position: 'absolute', left: 92, top: 48, fontFamily: 'GeistMono', fontSize: 16, letterSpacing: '0.22em', textTransform: 'uppercase', color: BRAND.sub }}>{eyebrow}</div>}
    <div style={{ position: 'absolute', left: 90, top: 78, fontFamily: 'InstrumentSerif', fontSize: 68, color: BRAND.ink, lineHeight: 1, transform: 'scaleX(1.2)', transformOrigin: 'left center' }}>
      {titleParts ? titleParts.map((p, i) => <span key={i} style={{ color: p.c ?? BRAND.ink }}>{p.t}</span>) : title}
    </div>
    {sub && <div style={{ position: 'absolute', left: 92, top: 162, fontFamily: 'GeistMono', fontSize: 19, letterSpacing: '0.04em', color: subColor ?? BRAND.link }}>{sub}</div>}
    <div style={{ position: 'absolute', left: 92, top: 210, width: W - 184, height: 1, background: BRAND.line }} />
    {logo === 'trustabl' ? (
      // Lockup = shield SVG + wordmark overlay (same technique as Bookends'
      // DemoIntro/DemoOutro). The wordmark has to follow the skin: -word-dark.svg fills
      // "Trust" near-white (#E8EBF0) for navy, -word.svg fills it navy (#1A3764) for light.
      // Using the wrong one makes "Trust" all but invisible — that is exactly what the
      // light skin regressed to before this was gated.
      // The two SVGs do not share a kerning origin, so each needs its own translateX;
      // -7px for light was solved by minimising pixel delta against out/g_scan.png.
      <div style={{ position: 'absolute', right: 92, top: 74, width: 300, height: 300 * 2492 / 10449 }}>
        <div style={{ position: 'relative', width: 300, height: 300 * 2492 / 10449, transform: 'translateX(10px)' }}>
          <Img src={staticFile('logos/trustabl-shield.svg')} style={{ position: 'absolute', left: 0, top: 0, width: 300 }} />
          <Img src={staticFile(LIGHT_SKIN ? 'logos/trustabl-word.svg' : 'logos/trustabl-word-dark.svg')} style={{ position: 'absolute', left: 0, top: 0, width: 300, transform: LIGHT_SKIN ? 'translateX(-7px)' : 'translateX(-19px)' }} />
        </div>
      </div>
    ) : logo ? (
      <div style={{ position: 'absolute', right: 92, top: 78, display: 'flex', alignItems: 'center', gap: 16 }}>
        <div style={{ height: 62, padding: LIGHT_SKIN ? 0 : '9px 16px', background: BRAND.logoChip, borderRadius: 10, display: 'flex', alignItems: 'center' }}>
          <Img src={staticFile('logos/' + logo + '.png')} style={{ height: LIGHT_SKIN ? 62 : 44, objectFit: 'contain' }} />
        </div>
        {LOGO_NAMES[logo] && <span style={{ fontFamily: 'GeistMono', fontSize: 27, color: BRAND.ink }}>{LOGO_NAMES[logo]}</span>}
      </div>
    ) : null}
    {ms && <MsMark />}
    {badge && <div style={{ position: 'absolute', left: 92, top: 168, padding: '7px 16px', border: `1px solid ${badgeColor}`, borderRadius: 6, fontFamily: 'GeistMono', fontSize: 14, letterSpacing: '0.08em', textTransform: 'uppercase', color: badgeColor, background: BRAND.panel }}>{badge}</div>}
  </>
);

const MsMark: React.FC = () => (
  <div style={{ position: 'absolute', right: 92, top: 78, display: 'flex', alignItems: 'center', gap: 14 }}>
    <MsGrid cell={26} />
    <span style={{ fontFamily: 'GeistMono', fontSize: 27, color: BRAND.ink }}>Microsoft</span>
  </div>
);
