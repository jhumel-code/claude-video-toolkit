import React from 'react';
import { Composition } from 'remotion';
import { Easing } from 'remotion';
import { TransitionSeries, linearTiming } from '@remotion/transitions';
import { slide } from '@remotion/transitions/slide';
import { fade } from '@remotion/transitions/fade';
import { Section, secFrames } from './Section';
import { Intro, Outro, IntroSound, IntroA, IntroB, IntroC, DemoIntro, DemoOutro, introFrames, outroFrames, introSoundFrames } from './Bookends';
import { SPECS } from './specs';
import { Spof, spofFrames } from './Spof';
import { FPS, K, CW, CH } from './brand';

const XF = K(22); // slide-transition frames between sections (no same-position header overlap)

type Item = { key: string; node: React.ReactNode; dur: number };

// intro + the 9 sections + outro
const ITEMS: Item[] = [
  { key: '_intro', node: <IntroA />, dur: introFrames },
  ...SPECS.map((s) => ({ key: s.id, node: <Section spec={s} />, dur: secFrames(s.audioDur) })),
  { key: '_outro', node: <Outro />, dur: outroFrames },
];
// The default for new videos: same intro + sections, no branded outro (the video ends
// on its last section).
const WORKING_ITEMS = ITEMS.slice(0, -1);

// One transition series: soft fade at the bookend edges, slide between content sections
// (a fade() between content sections superimposes their same-position headers).
const chain = (items: Item[], hasOutro: boolean): React.FC => () => (
  <TransitionSeries>
    {items.map((it, i) => {
      const bookendEdge = i === 1 || (hasOutro && i === items.length - 1);
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
const total = (items: Item[]) => items.reduce((a, it) => a + it.dur, 0) - XF * (items.length - 1);

const Explainer = chain(ITEMS, true);
const ExplainerWorking = chain(WORKING_ITEMS, false);

export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="Explainer" component={Explainer} durationInFrames={total(ITEMS)} fps={FPS} width={CW} height={CH} />
    <Composition id="ExplainerWorking" component={ExplainerWorking} durationInFrames={total(WORKING_ITEMS)} fps={FPS} width={CW} height={CH} />
    <Composition id="Spof" component={Spof} durationInFrames={spofFrames} fps={FPS} width={CW} height={CH} />
    <Composition id="Intro" component={Intro} durationInFrames={introFrames} fps={FPS} width={CW} height={CH} />
    <Composition id="Outro" component={Outro} durationInFrames={outroFrames} fps={FPS} width={CW} height={CH} />
    <Composition id="IntroSound" component={IntroSound} durationInFrames={introSoundFrames} fps={FPS} width={CW} height={CH} />
    <Composition id="IntroA" component={IntroA} durationInFrames={introFrames} fps={FPS} width={CW} height={CH} />
    <Composition id="IntroB" component={IntroB} durationInFrames={introFrames} fps={FPS} width={CW} height={CH} />
    <Composition id="IntroC" component={IntroC} durationInFrames={introFrames} fps={FPS} width={CW} height={CH} />
    {/* The official terminal-demo bookends (dark terminal background). DemoIntro is what
        the toolkit ships pre-rendered as assets/trustabl-intro.mp4. */}
    <Composition id="DemoIntro" component={DemoIntro} durationInFrames={introFrames} fps={FPS} width={CW} height={CH} />
    <Composition id="DemoOutro" component={DemoOutro} durationInFrames={outroFrames} fps={FPS} width={CW} height={CH} />
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
