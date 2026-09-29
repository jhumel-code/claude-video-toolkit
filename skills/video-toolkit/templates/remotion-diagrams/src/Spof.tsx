// Spof.tsx — 16:9 proving example for the network primitives: the "Single Point
// of Failure" explainer as a slide deck. Three scenes (one path → two paths →
// closing card) joined by the Explainer's slide/fade transitions, laid out in the
// same W×H design space Section uses. Beat timing derives from the measured
// narration clips (public/audio/spof_1..4.mp3) so state flips land on the voiceover.
import React from 'react';
import { AbsoluteFill, Audio, Easing, Sequence, staticFile } from 'remotion';
import { TransitionSeries, linearTiming } from '@remotion/transitions';
import { slide } from '@remotion/transitions/slide';
import { fade } from '@remotion/transitions/fade';
import { Bg, Reveal, Header } from './components';
import { FontLoader } from './fonts';
import { BRAND, FPS, K, W, H, CW, CH } from './brand';
import { NARRATION } from './narration.gen';
import { FlowEdge, RingNode, AppNode, SourceCard, StatCard, TagPill, CaptionPill, EdgeLayer, rgba } from './network';

const F = (s: number) => Math.round(s * FPS);

// same 16:10 → 16:9 height-fit Section uses (uniform scale, dot paper fills gutters)
const S = CH / H, OX = (CW - W * S) / 2, OY = (CH - H * S) / 2;
const Fit: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <AbsoluteFill>
    <FontLoader />
    <Bg />
    <div style={{ position: 'absolute', left: 0, top: 0, width: W, height: H, transform: `translate(${OX}px, ${OY}px) scale(${S})`, transformOrigin: '0 0' }}>
      {children}
    </div>
  </AbsoluteFill>
);

const Head: React.FC = () => (
  <Header eyebrow="Trustabl · systems explainer"
    titleParts={[{ t: 'Single Point ' }, { t: 'of Failure', c: BRAND.danger }]}
    sub="when one shared edge takes down half the internet" />
);

// narration clip durations (voice.py writes them to narration.gen.ts) + breathing gaps
const D1 = NARRATION.spof_1.dur, D2 = NARRATION.spof_2.dur, D3 = NARRATION.spof_3.dur, D4 = NARRATION.spof_4.dur;
const B1 = 0.6, B2 = B1 + D1 + 0.4;            // scene 1 beats
const S1 = B2 + D2 + 1.3;
const C1 = 0.75, C2 = C1 + D3 + 0.4;           // scene 2 beats (transition eats ~0.7s)
const S2 = C2 + D4 + 1.0;
const S3 = 2.8;                                 // closing card
const XF = K(22);
export const spofFrames = F(S1) + F(S2) + F(S3) - 2 * XF;

const APPS = ['X', 'Reddit', 'Discord', 'Zoom', 'Canva'];
const ROWS = [460, 620, 780, 940, 1100];        // shared app column: continuity across the slide
const AX = 1750;
const EDGE = 1.25;                              // FlowEdge size multiplier for the big canvas

const STAT_XS = [500, 1200, 1900];

const OnePath: React.FC = () => {
  const die = [{ at: B2, s: 'dead' as const }];
  const down = [{ at: B2, s: 'down' as const }];
  return (
    <Fit>
      <Reveal at={F(0.1)}><Head /></Reveal>
      <Reveal at={F(B1)}>
        <TagPill x={430} y={320} label="ONE PATH" text="every app rides one shared edge" color={BRAND.danger} />
        <EdgeLayer w={W} h={H}>
          <FlowEdge x1={470} y1={780} x2={878} y2={780} states={die} particles={2} seed={9} bend={0.4} size={EDGE} />
          {ROWS.map((y, i) => <FlowEdge key={i} x1={1022} y1={780} x2={1720} y2={y} states={die} seed={i} size={EDGE} />)}
        </EdgeLayer>
        <SourceCard x={330} y={780} w={280} h={120} fs={28} title="TRAFFIC" sub="5 apps" />
        <RingNode x={950} y={780} r={72} labelTop="SHARED EDGE" subLive="single dependency" states={down} />
        {APPS.map((n, i) => <AppNode key={n} x={AX} y={ROWS[i]} name={n} states={[{ at: B2 + 0.1 + i * 0.06, s: 'down' }]} />)}
      </Reveal>
      <Reveal at={F(B1 + 1.7)} dy={14}>
        <TagPill x={950} y={955} label="cut this one" text="= ?" color={BRAND.danger} />
      </Reveal>
      {[
        { label: 'PATHS', value: '1' },
        { label: 'DEPENDENCY', value: 'shared' },
        { label: 'RESULT', value: '5 DOWN' },
      ].map((c, i) => (
        <Reveal key={c.label} at={F(B2 + 1.1 + i * 0.18)} dy={18}>
          <StatCard x={STAT_XS[i]} y={1330} w={430} h={150} fs={40} label={c.label} value={c.value} color={BRAND.danger} />
        </Reveal>
      ))}
      <Reveal at={F(B1)}>
        <CaptionPill x={W / 2} y={1447} items={[
          { at: B1, t: 'every app here rides ONE shared edge' },
          { at: B2, t: 'cut that one edge, and they ALL go dark at once' },
        ]} />
      </Reveal>
      <Sequence from={F(B1)}><Audio src={staticFile('audio/spof_1.mp3')} /></Sequence>
      <Sequence from={F(B2)}><Audio src={staticFile('audio/spof_2.mp3')} /></Sequence>
    </Fit>
  );
};

const TwoPaths: React.FC = () => {
  const die = [{ at: C2, s: 'dead' as const }];
  const down = [{ at: C2, s: 'down' as const }];
  return (
    <Fit>
      <Head />
      <Reveal at={F(C1)}>
        <TagPill x={450} y={320} label="TWO PATHS" text="a second independent edge" color={BRAND.accent} />
        <EdgeLayer w={W} h={H}>
          <FlowEdge x1={470} y1={780} x2={886} y2={560} states={die} particles={2} seed={21} bend={0.4} size={EDGE} />
          <FlowEdge x1={470} y1={780} x2={886} y2={1000} particles={2} seed={22} bend={0.4} color={BRAND.accent} size={EDGE} />
          {ROWS.map((y, i) => <FlowEdge key={'p' + i} x1={1014} y1={560} x2={1720} y2={y} states={die} seed={i + 3} size={EDGE} />)}
          {ROWS.map((y, i) => <FlowEdge key={'b' + i} x1={1014} y1={1000} x2={1720} y2={y} seed={i + 8} color={BRAND.accent} size={EDGE} />)}
        </EdgeLayer>
        <SourceCard x={330} y={780} w={280} h={120} fs={28} title="TRAFFIC" sub="5 apps" />
        <RingNode x={950} y={560} r={64} labelTop="PRIMARY" states={down} />
        <RingNode x={950} y={1000} r={64} subLive="BACKUP · independent" subColor={BRAND.accent} liveColor={BRAND.accent} />
        {APPS.map((n, i) => <AppNode key={n} x={AX} y={ROWS[i]} name={n} />)}
      </Reveal>
      {[
        { label: 'PATHS', value: '2' },
        { label: 'DEPENDENCY', value: 'none' },
        { label: 'RESULT', value: 'ALL UP' },
      ].map((c, i) => (
        <Reveal key={c.label} at={F(C2 + 1.4 + i * 0.18)} dy={18}>
          <StatCard x={STAT_XS[i]} y={1330} w={430} h={150} fs={40} label={c.label} value={c.value} color={BRAND.accent} />
        </Reveal>
      ))}
      <Reveal at={F(C1)}>
        <CaptionPill x={W / 2} y={1447} items={[
          { at: C1, t: 'add a second independent path' },
          { at: C2, t: 'redundancy: no single thing left to kill' },
        ]} />
      </Reveal>
      <Sequence from={F(C1)}><Audio src={staticFile('audio/spof_3.mp3')} /></Sequence>
      <Sequence from={F(C2)}><Audio src={staticFile('audio/spof_4.mp3')} /></Sequence>
    </Fit>
  );
};

const Close: React.FC = () => (
  <Fit>
    <Reveal at={F(0.15)} dy={16}>
      <div style={{ position: 'absolute', left: 0, top: 660, width: W, textAlign: 'center', fontFamily: 'GeistMono', fontWeight: 700, fontSize: 36, letterSpacing: '0.22em', color: BRAND.ink }}>
        RESILIENCE&nbsp;&nbsp;=&nbsp;&nbsp;NO SINGLE POINT
      </div>
      <div style={{ position: 'absolute', left: W / 2 - 40, top: 740, width: 80, height: 2, background: BRAND.accent }} />
      <div style={{ position: 'absolute', left: 0, top: 772, width: W, textAlign: 'center', fontFamily: 'GeistMono', fontSize: 20, letterSpacing: '0.30em', color: rgba(BRAND.ink, 0.45) }}>
        CLOUDFLARE · X · DISCORD · ZOOM · AWS
      </div>
    </Reveal>
  </Fit>
);

export const Spof: React.FC = () => (
  <TransitionSeries>
    <TransitionSeries.Sequence durationInFrames={F(S1)}><OnePath /></TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: XF, easing: Easing.inOut(Easing.cubic) })} presentation={slide({ direction: 'from-right' })} />
    <TransitionSeries.Sequence durationInFrames={F(S2)}><TwoPaths /></TransitionSeries.Sequence>
    <TransitionSeries.Transition timing={linearTiming({ durationInFrames: XF, easing: Easing.inOut(Easing.cubic) })} presentation={fade()} />
    <TransitionSeries.Sequence durationInFrames={F(S3)}><Close /></TransitionSeries.Sequence>
  </TransitionSeries>
);
