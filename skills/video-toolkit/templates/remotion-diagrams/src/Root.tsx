import React from 'react';
import { Composition } from 'remotion';
import { Easing } from 'remotion';
import { TransitionSeries, linearTiming } from '@remotion/transitions';
import { slide } from '@remotion/transitions/slide';
import { fade } from '@remotion/transitions/fade';
import { Section, secFrames } from './Section';
import { Intro, Outro, IntroSound, IntroA, IntroB, IntroC, introFrames, outroFrames, introSoundFrames } from './Bookends';
import { SPECS } from './specs';
import { FPS, CW, CH } from './brand';

const XF = 22; // slide-transition frames between sections (no same-position header overlap)

// intro + the 9 sections + outro, joined as one transition series
const ITEMS = [
  { key: '_intro', node: <IntroA />, dur: introFrames },
  ...SPECS.map((s) => ({ key: s.id, node: <Section spec={s} />, dur: secFrames(s.audioDur) })),
  { key: '_outro', node: <Outro />, dur: outroFrames },
];

const Explainer: React.FC = () => (
  <TransitionSeries>
    {ITEMS.map((it, i) => {
      // soft fade into the intro-edge and out to the outro-edge; slide between content sections
      const bookendEdge = i === 1 || i === ITEMS.length - 1;
      return (
        <React.Fragment key={it.key}>
          {i > 0 && (
            <TransitionSeries.Transition
              timing={linearTiming({ durationInFrames: XF, easing: Easing.inOut(Easing.cubic) })}
              presentation={bookendEdge ? fade() : slide({ direction: 'from-right' })}
            />
          )}
          <TransitionSeries.Sequence durationInFrames={it.dur}>{it.node}</TransitionSeries.Sequence>
        </React.Fragment>
      );
    })}
  </TransitionSeries>
);

const TOTAL = ITEMS.reduce((a, it) => a + it.dur, 0) - XF * (ITEMS.length - 1);

export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="Explainer" component={Explainer} durationInFrames={TOTAL} fps={FPS} width={CW} height={CH} />
    <Composition id="Intro" component={Intro} durationInFrames={introFrames} fps={FPS} width={CW} height={CH} />
    <Composition id="Outro" component={Outro} durationInFrames={outroFrames} fps={FPS} width={CW} height={CH} />
    <Composition id="IntroSound" component={IntroSound} durationInFrames={introSoundFrames} fps={FPS} width={CW} height={CH} />
    <Composition id="IntroA" component={IntroA} durationInFrames={introFrames} fps={FPS} width={CW} height={CH} />
    <Composition id="IntroB" component={IntroB} durationInFrames={introFrames} fps={FPS} width={CW} height={CH} />
    <Composition id="IntroC" component={IntroC} durationInFrames={introFrames} fps={FPS} width={CW} height={CH} />
    {SPECS.map((s) => (
      <Composition
        key={s.id}
        id={s.id}
        component={Section}
        defaultProps={{ spec: s }}
        durationInFrames={secFrames(s.audioDur)}
        fps={FPS}
        width={CW}
        height={CH}
      />
    ))}
  </>
);
