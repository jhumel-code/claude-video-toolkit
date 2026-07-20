import React from 'react';
import { AbsoluteFill, Audio, Sequence, staticFile } from 'remotion';
import { Bg, Reveal, Node, Pill, Arrow, ArrowSvg, MonoCard, Header } from './components';
import { FontLoader } from './fonts';
import { FPS, K, W, H, CW, CH } from './brand';
import type { Spec } from './specs';

export const secFrames = (audioDur: number) => Math.round((0.5 + audioDur + 1.5) * FPS);

// fit the 16:10 design (W×H) into the 16:9 canvas (CW×CH) by height — uniform scale, no
// distortion; the dot-paper Bg fills the side gutters so it reads as comfortable margin.
const S = CH / H;
const OX = (CW - W * S) / 2;
const OY = (CH - H * S) / 2;

export const Section: React.FC<{ spec: Spec }> = ({ spec }) => {
  const N = spec.groups.length;
  // narration-synced reveals: the audio starts at frame 15, so a voiceover-time T(s) lands at
  // frame 15 + T*FPS. When spec.focalAt is set, the source (group 0) appears first, the focal
  // artifact card + its content (group 1, mono via ri=1) fire the moment it's named, and the
  // rest spread out afterward to ~80% of the voiceover. Sections without focalAt (overview)
  // fall back to an even spread.
  const FF = spec.focalAt != null ? Math.round(K(15) + spec.focalAt * FPS) : null;
  const lastE = Math.floor(0.8 * spec.audioDur * FPS);
  const lastF = K(15) + Math.floor(0.8 * spec.audioDur * FPS);
  const at = (i: number) => {
    if (FF == null) return N <= 1 ? K(18) : Math.round(K(18) + (lastE - K(18)) * (i / (N - 1)));
    if (i <= 0) return K(18);
    if (i === 1) return FF;
    return Math.round(FF + (lastF - FF) * ((i - 1) / Math.max(1, N - 2)));
  };
  return (
    <AbsoluteFill>
      <FontLoader />
      <Bg />
      <div style={{ position: 'absolute', left: 0, top: 0, width: W, height: H, transform: `translate(${OX}px, ${OY}px) scale(${S})`, transformOrigin: '0 0' }}>
        <Header eyebrow={spec.eyebrow} title={spec.title} logo={spec.logo} ms={spec.ms} badge={spec.badge} badgeColor={spec.badgeColor} />
        {spec.groups.map((g, i) => {
          // per-section balance: diagram groups are centered (dx) + lifted (dy) to fill the
          // 16:9 frame; the code card stays horizontally centered (dx=0) but lifts with dy.
          const tx = g.mono ? 0 : (spec.dx || 0);
          const ty = spec.dy || 0;
          // the code card (mono = the file's content) reveals WITH the focal/key card (group 1),
          // so a file's content is on screen the moment its card appears.
          const ri = g.mono ? Math.min(1, N - 1) : i;
          // a group may pin its own reveal to a voiceover second (atSec) — used for the
          // overview thesis caption, which the narrator states up front, not at the end.
          const explicit = g.atSec != null ? Math.round(K(15) + g.atSec * FPS) : null;
          return (
            <Reveal key={i} at={explicit ?? at(ri)}>
              <div style={{ position: 'absolute', inset: 0, transform: `translate(${tx}px, ${ty}px)` }}>
                {g.arrows && <ArrowSvg>{g.arrows.map((a, j) => <Arrow key={j} {...a} />)}</ArrowSvg>}
                {g.nodes && g.nodes.map((n, j) => <Node key={j} {...n} />)}
                {g.pills && g.pills.map((p, j) => <Pill key={j} {...p} />)}
                {g.mono && <MonoCard {...g.mono} />}
              </div>
            </Reveal>
          );
        })}
      </div>
      <Sequence from={K(15)}><Audio src={staticFile('audio/' + spec.audio)} /></Sequence>
    </AbsoluteFill>
  );
};
