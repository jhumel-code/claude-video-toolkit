# Remotion animated diagram explainers

A higher-fidelity engine for **narrated, animated, branded diagram explainers**
("what are these artifacts / why do they matter"). Complements the Pillow/VHS
pipeline: use this when you want editorial-grade diagrams with smooth native
animation; use Pillow when you want zero extra dependencies.

## What it is
- **Engine**: [Remotion](https://www.remotion.dev) (React → video). Template lives in
  `templates/remotion-diagrams/`.
- **Visual language**: the [diagram-design](https://github.com/cathrynlavery/diagram-design)
  system (MIT) — Instrument Serif titles, Geist Sans labels, Geist Mono technical,
  eyebrow tags, hairline rules, one accent-tint focal node per figure — mapped to a
  brand in `src/brand.ts`.
- **Data-driven**: each section is a `Spec` (header + ordered `groups[]` of
  nodes/arrows/pills/mono). A generic `Section` component reveals each group with an
  ease-out fade+slide, **paced across the section's voiceover and finished by ~80%** so
  no detail pops in at the cut. Sections join via `@remotion/transitions` **`slide()`**
  — never `fade()` between content sections: a crossfade superimposes the two sections'
  same-position headers for the overlap and garbles them (invisible in mid-section
  stills, only visible on the transition frames). `fade()` is fine at the bookend edges.

## Why it beats the Pillow path for this
- Real `interpolate`/`spring` animation + `TransitionSeries` transitions (no hand-rolled
  ffmpeg xfade chains).
- CSS-gradient backgrounds render smooth — **no 8-bit banding** (a recurring Pillow
  pain point; see [[10-style-guide]] and the dither/deband workarounds it needed).
- HTML/SVG means the diagram-design language drops in directly.

## Workflow
See `templates/remotion-diagrams/README.md`. In short: write the script in
`narration.json`, run `python scripts/voice.py <project>` (audio + `narration.gen.ts`
with every duration and sentence cue), edit `src/specs.tsx`,
QA with `npx remotion still ... --scale=0.5`, then
`npx remotion render src/index.ts ExplainerWorking out/explainer.mp4` (IntroA + sections,
no outro: the default shape; `Explainer` adds the branded outro).
4K: `--scale=1.5 --crf=10 --concurrency=2`, started in the background.

## Keeping the template current
The live Trustabl project the template came from evolves; re-sync the engine files
(`brand.ts`, `components.tsx`, `Section.tsx`, `Bookends.tsx`, `fonts.ts`, `network.tsx`,
`Spof.tsx`, `specs.tsx`) when it improves, and check the shipped mp3s still match the
specs' `audioDur` (a 2026-09-29 sync found them 6.9 s apart on one section, and IntroA
drawing "Trust" navy-on-navy). `Root.tsx` is the template's own: it registers only the
template's compositions.

## Skins and bookends
`src/brand.ts` holds two skins with identical token names: navy (default) and the
original light skin (`REMOTION_SKIN=light`); any other value throws. Bookends:
`IntroA` opens explainers; `DemoIntro` / `DemoOutro` are the dark terminal-demo bookends
(`DemoIntro` ships pre-rendered as `assets/trustabl-intro.mp4`, the official intro).

## Template codenames
The template is versioned by codename + git tag; the directory at HEAD is the
default. **Headway (v3, default)** (`template/headway-v3`) = Slipstream plus narration as
data: `narration.json` voiced by `scripts/voice.py`, which writes `narration.gen.ts` so
`audioDur` and every reveal (`cue(id, n, frac)`) follow the measured audio (see
`14-narration-voice.md`). **Slipstream (v2)** (`template/slipstream-v2.1`, with the
2026-09-29 fixes; `template/slipstream-v2`) = everything below with hand-typed timings.
**Harbor (v1)** = the reveal-only Section/spec model before the network primitives
(`template/harbor-v1`).

## Network primitives (Slipstream, 2026-07-26)
`src/network.tsx` adds a second, **stateful** visual language for network/topology
explainers (content styling borrowed from the social "single point of failure"
format, rendered in the system's own 16:9 canvas): curved **`FlowEdge`** bezier
edges with particles riding them, **`RingNode`** hubs and **`AppNode`** endpoints
that flip `live → down` mid-scene, **`StatCard`** / **`TagPill`** / timed
**`CaptionPill`** (subtitle beats). `Header` gained `titleParts` (two-tone title)
and `sub`. Unlike the Section/spec model (reveal-only), these components take a
`states`/`items` **timeline in seconds from the enclosing Sequence start**, so a
node can fail, recover, or re-route on the narration beat. `src/Spof.tsx` is the
proving example (`Spof`, standard CW×CH canvas): three slides joined by the
Explainer's slide/fade `TransitionSeries` — one shared edge failing (everything
OFFLINE), a second independent path keeping the apps LIVE, then a closing card.
Beat times derive from the measured narration clip durations
(`public/audio/spof_1..4.mp3`), the same discipline as `specs.tsx` `audioDur`.
Reuse the pattern: keep reveals for *appearing*, state timelines for *changing*,
pin both to narration seconds, and change slides with `TransitionSeries` (slide
between content scenes, fade at bookend edges). The primitives are
resolution-agnostic — `VHeader` (centered two-tone header) exists for 9:16
vertical cuts if a social format is ever needed.

## Licensing (read before commercial use)
Remotion is **source-available, not free for all**: free for individuals, non-profits,
and for-profit companies with **≤3 employees**; larger companies need a paid Company
License (~$75/mo). The Pillow pipeline remains the $0 fallback. The diagram-design
language and the digitalsamba toolkit it's modeled on are both MIT.
