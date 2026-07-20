import React from 'react';
import { AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame, interpolate, Easing, Img } from 'remotion';
import { Bg } from './components';
import { FontLoader } from './fonts';
import { BRAND, FPS, K } from './brand';

export const introFrames = Math.round((2.946 + 1.35) * FPS); // SFX ident + short logo hold (no narration)
export const outroFrames = Math.round((0.5 + 8.16 + 1.5) * FPS);

const center: React.CSSProperties = {
  position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column',
  alignItems: 'center', justifyContent: 'center', textAlign: 'center',
};

const useReveal = () => {
  const f = useCurrentFrame();
  return interpolate(f, [K(6), K(30)], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic) });
};

// ---- intro: clean slide, Trustabl logo + wordmark centered ----
export const Intro: React.FC = () => {
  const p = useReveal();
  return (
    <AbsoluteFill>
      <FontLoader />
      <Bg />
      <div style={{ ...center, opacity: p, transform: `translateY(${(1 - p) * 24}px)` }}>
        <Img src={staticFile('logos/trustabl.png')} style={{ height: 210, objectFit: 'contain', marginBottom: 28 }} />
        <div style={{ fontFamily: 'InstrumentSerif', fontSize: 150, color: BRAND.ink, lineHeight: 1, transform: 'scaleX(1.1)' }}>Trustabl</div>
      </div>
      <Sequence from={K(4)}><Audio src={staticFile('audio/sy_intro_sfx.mp3')} /></Sequence>
    </AbsoluteFill>
  );
};

// ---- intro proposal: same logo+wordmark, NO narration (a sound sting is muxed in later) ----
export const introSoundFrames = Math.round(6.0 * FPS);
export const IntroSound: React.FC = () => {
  const f = useCurrentFrame();
  const fin = interpolate(f, [K(6), K(30)], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic) });
  const fout = interpolate(f, [K(162), K(180)], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  return (
    <AbsoluteFill>
      <FontLoader />
      <Bg />
      <div style={{ ...center, opacity: fin * fout, transform: `translateY(${(1 - fin) * 24}px)` }}>
        <Img src={staticFile('logos/trustabl.png')} style={{ height: 210, objectFit: 'contain', marginBottom: 28 }} />
        <div style={{ fontFamily: 'InstrumentSerif', fontSize: 150, color: BRAND.ink, lineHeight: 1, transform: 'scaleX(1.1)' }}>Trustabl</div>
      </div>
    </AbsoluteFill>
  );
};

// ---- intro animation proposals (logo + wordmark + the ident SFX, different motion) ----
const EO = (f: number, a: number, b: number, from: number, to: number) =>
  interpolate(f, [K(a), K(b)], [from, to], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic) });
const SFX: React.FC = () => <Sequence from={K(4)}><Audio src={staticFile('audio/sy_intro_sfx.mp3')} /></Sequence>;
const LW = 1520; // lockup display width (svg viewBox is 10449x2492)
const LFull: React.FC = () => <Img src={staticFile('logos/trustabl-lockup.svg')} style={{ width: LW }} />;
const LShield: React.FC<{ st?: React.CSSProperties; w?: number }> = ({ st, w = LW }) => <Img src={staticFile('logos/trustabl-shield.svg')} style={{ position: 'absolute', left: 0, top: 0, width: w, ...st }} />;
const LWord: React.FC<{ st?: React.CSSProperties; w?: number }> = ({ st, w = LW }) => <Img src={staticFile('logos/trustabl-word.svg')} style={{ position: 'absolute', left: 0, top: 0, width: w, ...st }} />;

// A — staggered: shield first, then the wordmark
export const IntroA: React.FC = () => {
  const f = useCurrentFrame();
  const sm = (a: number, b: number, from: number, to: number) =>
    interpolate(f, [K(a), K(b)], [from, to], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic) });
  const sc = sm(8, 58, 0.965, 1);          // whole lockup eases up gently
  const ps = sm(8, 44, 0, 1);              // shield cross-fades in
  const pw = sm(26, 62, 0, 1);             // wordmark cross-fades in, overlapping (blended)
  const out = interpolate(f, [K(114), K(128)], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }); // soft exit
  const G = 95; // shield +G/2, word -G/2 keeps the tightened lockup centered
  return (
    <AbsoluteFill><FontLoader /><Bg />
      <div style={{ ...center, opacity: out }}>
        <div style={{ transform: `scale(${0.8 * sc})` }}>
          <div style={{ position: 'relative', width: LW, height: LW * 2492 / 10449, transform: `translateX(${G / 2}px)` }}>
            <LShield st={{ opacity: ps }} />
            <LWord st={{ opacity: pw, transform: `translateX(${-G}px)` }} />
          </div>
        </div>
      </div>
      <SFX />
    </AbsoluteFill>
  );
};

// ---- DARK bookends for the terminal demo (blend with the dark #0D1B2A terminal bg) ----
const DarkBg: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: '#0D1B2A' }}>
    <AbsoluteFill style={{ backgroundImage: 'radial-gradient(rgba(255,255,255,0.09) 1.5px, transparent 1.6px)', backgroundSize: '34px 34px' }} />
  </AbsoluteFill>
);
const LWordDark: React.FC<{ st?: React.CSSProperties; w?: number }> = ({ st, w = LW }) => <Img src={staticFile('logos/trustabl-word-dark.svg')} style={{ position: 'absolute', left: 0, top: 0, width: w, ...st }} />;

// DemoIntro — IntroA on the dark terminal background, light wordmark.
export const DemoIntro: React.FC = () => {
  const f = useCurrentFrame();
  const sm = (a: number, b: number, from: number, to: number) =>
    interpolate(f, [K(a), K(b)], [from, to], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic) });
  const sc = sm(8, 58, 0.965, 1);
  const ps = sm(8, 44, 0, 1);
  const pw = sm(26, 62, 0, 1);
  const out = interpolate(f, [K(114), K(128)], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const G = 95;
  return (
    <AbsoluteFill><FontLoader /><DarkBg />
      <div style={{ ...center, opacity: out }}>
        <div style={{ transform: `scale(${0.8 * sc})` }}>
          <div style={{ position: 'relative', width: LW, height: LW * 2492 / 10449, transform: `translateX(${G / 2}px)` }}>
            <LShield st={{ opacity: ps }} />
            <LWordDark st={{ opacity: pw, transform: `translateX(${-G}px)` }} />
          </div>
        </div>
      </div>
      <SFX />
    </AbsoluteFill>
  );
};

// B — scale-in & settle: whole mark zooms in slightly and settles
export const IntroB: React.FC = () => {
  const f = useCurrentFrame();
  const p = EO(f, 6, 34, 0, 1), s = EO(f, 6, 42, 1.06, 1);
  return (
    <AbsoluteFill><FontLoader /><Bg />
      <div style={{ ...center, opacity: p, transform: `scale(${s})` }}><LFull /></div>
      <SFX />
    </AbsoluteFill>
  );
};

// C — rise + accent glow that pulses on the hit
export const IntroC: React.FC = () => {
  const f = useCurrentFrame();
  const p = EO(f, 6, 32, 0, 1), rise = EO(f, 6, 32, 46, 0);
  const glow = interpolate(f, [K(8), K(24), K(52)], [0, 0.5, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  return (
    <AbsoluteFill><FontLoader /><Bg />
      <AbsoluteFill style={{ alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ width: 1200, height: 1200, borderRadius: '50%', background: `radial-gradient(circle, rgba(81,193,181,${glow}) 0%, rgba(81,193,181,0) 60%)`, filter: 'blur(50px)' }} />
      </AbsoluteFill>
      <div style={{ ...center, opacity: p, transform: `translateY(${rise}px)` }}><LFull /></div>
      <SFX />
    </AbsoluteFill>
  );
};

// ---- outro: Trustabl lockup + integration logos + visit CTA ----
const MsSquares: React.FC = () => (
  <div style={{ display: 'grid', gridTemplateColumns: '35px 35px', gridTemplateRows: '35px 35px', gap: 6 }}>
    {['#F25022', '#7FBA00', '#00A4EF', '#FFB900'].map((c) => <div key={c} style={{ background: c }} />)}
  </div>
);
const INTEGRATIONS: { img?: string; ms?: boolean; name: string }[] = [
  { img: 'opa', name: 'OPA' },
  { ms: true, name: 'Microsoft' },
  { img: 'nvidia', name: 'NVIDIA' },
  { img: 'owasp', name: 'OWASP' },
  { img: 'intoto', name: 'in-toto' },
  { img: 'cncf', name: 'CNCF' },
];

export const Outro: React.FC = () => {
  const f = useCurrentFrame();
  const sm = (a: number, b: number) => interpolate(f, [K(a), K(b)], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic) });
  const pLock = sm(8, 46), pRow = sm(34, 74), pVisit = sm(56, 96);
  return (
    <AbsoluteFill>
      <FontLoader />
      <Bg />
      <div style={{ position: 'absolute', top: 400, left: 0, width: '100%', display: 'flex', justifyContent: 'center', opacity: pLock, transform: `translateY(${(1 - pLock) * 16}px)` }}>
        <div style={{ position: 'relative', width: 690, height: 690 * 2492 / 10449, transform: 'translateX(23px)' }}>
          <LShield w={690} />
          <LWord w={690} st={{ transform: 'translateX(-46px)' }} />
        </div>
      </div>
      <div style={{ position: 'absolute', top: 640, left: 0, width: '100%', textAlign: 'center', opacity: pRow, transform: `translateY(${(1 - pRow) * 16}px)` }}>
        <div style={{ fontFamily: 'GeistMono', fontSize: 19, letterSpacing: '0.24em', textTransform: 'uppercase', color: BRAND.soft, marginBottom: 42 }}>Works with</div>
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'flex-end', gap: 52 }}>
          {INTEGRATIONS.map((it, i) => (
            <div key={i} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 20, width: 244 }}>
              <div style={{ height: 90, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                {it.ms ? <MsSquares /> : <Img src={staticFile('logos/' + it.img + '.png')} style={{ maxHeight: 90, maxWidth: 172, objectFit: 'contain' }} />}
              </div>
              <div style={{ fontFamily: 'GeistMono', fontSize: 26, color: BRAND.sub }}>{it.name}</div>
            </div>
          ))}
        </div>
      </div>
      <div style={{ position: 'absolute', top: 1085, left: 0, width: '100%', textAlign: 'center', opacity: pVisit, transform: `translateY(${(1 - pVisit) * 16}px)` }}>
        <div style={{ display: 'inline-block', fontFamily: 'InstrumentSerif', fontSize: 64, color: BRAND.ink, lineHeight: 1, transform: 'scaleX(1.2)' }}>
          Visit our website <span style={{ color: '#51C1B5' }}>trustabl.ai</span> for more information.
        </div>
      </div>
      <Sequence from={K(15)}><Audio src={staticFile('audio/sy_outro.mp3')} /></Sequence>
    </AbsoluteFill>
  );
};

// DemoOutro — Outro on the dark terminal background. Integration logos sit on
// light chips so dark marks (OPA, OWASP, in-toto) still read; text goes light.
export const DemoOutro: React.FC = () => {
  const f = useCurrentFrame();
  const sm = (a: number, b: number) => interpolate(f, [K(a), K(b)], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic) });
  const pLock = sm(8, 46), pRow = sm(34, 74), pVisit = sm(56, 96);
  return (
    <AbsoluteFill>
      <FontLoader />
      <DarkBg />
      <div style={{ position: 'absolute', top: 400, left: 0, width: '100%', display: 'flex', justifyContent: 'center', opacity: pLock, transform: `translateY(${(1 - pLock) * 16}px)` }}>
        <div style={{ position: 'relative', width: 690, height: 690 * 2492 / 10449, transform: 'translateX(23px)' }}>
          <LShield w={690} />
          <LWordDark w={690} st={{ transform: 'translateX(-46px)' }} />
        </div>
      </div>
      <div style={{ position: 'absolute', top: 640, left: 0, width: '100%', textAlign: 'center', opacity: pRow, transform: `translateY(${(1 - pRow) * 16}px)` }}>
        <div style={{ fontFamily: 'GeistMono', fontSize: 19, letterSpacing: '0.24em', textTransform: 'uppercase', color: 'rgba(232,235,240,0.55)', marginBottom: 42 }}>Works with</div>
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'flex-end', gap: 40 }}>
          {INTEGRATIONS.map((it, i) => (
            <div key={i} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 18, width: 200 }}>
              <div style={{ height: 104, width: 200, background: '#ffffff', borderRadius: 12, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '0 22px', boxSizing: 'border-box' }}>
                {it.ms ? <MsSquares /> : <Img src={staticFile('logos/' + it.img + '.png')} style={{ maxHeight: 64, maxWidth: 150, objectFit: 'contain' }} />}
              </div>
              <div style={{ fontFamily: 'GeistMono', fontSize: 24, color: 'rgba(232,235,240,0.82)' }}>{it.name}</div>
            </div>
          ))}
        </div>
      </div>
      <div style={{ position: 'absolute', top: 1085, left: 0, width: '100%', textAlign: 'center', opacity: pVisit, transform: `translateY(${(1 - pVisit) * 16}px)` }}>
        <div style={{ display: 'inline-block', fontFamily: 'InstrumentSerif', fontSize: 64, color: '#E8EBF0', lineHeight: 1, transform: 'scaleX(1.2)' }}>
          Visit our website <span style={{ color: '#51C1B5' }}>trustabl.ai</span> for more information.
        </div>
      </div>
      <Sequence from={K(15)}><Audio src={staticFile('audio/sy_outro.mp3')} /></Sequence>
    </AbsoluteFill>
  );
};
