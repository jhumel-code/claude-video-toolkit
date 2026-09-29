# Remotion animated diagram explainer (template)

> **Codename: Headway (v3), the default template.** The narration is data
> (`narration.json`), written to sound like a person and voiced by `scripts/voice.py`
> (Kokoro by default), and every section length and reveal time comes from the measured
> audio. Older versions are git-tagged: `template/slipstream-v2.1` (v2 with the
> 2026-09-29 fixes), `template/slipstream-v2`, `template/harbor-v1`.

A **Remotion**-based engine for narrated, animated, branded diagram explainers — the
"what are these artifacts and why do they matter" style video. Each section is a
**data spec** (nodes / arrows / a mono code card), rendered by a generic `Section`
component with eased reveals paced to the section's voiceover, joined by native
slide transitions (`fade()` only at the bookend edges — crossfading content sections
superimposes their same-position headers).

Adopts the **diagram-design** visual language (Instrument Serif titles, Geist Sans
labels, Geist Mono technical, eyebrow tags, hairline rules, one accent-tint focal
node) mapped onto a brand via `src/brand.ts`.

## Why Remotion (vs the Pillow path)
Native animation (`interpolate`/`spring`), real CSS-gradient backgrounds (no 8-bit
banding), `TransitionSeries` crossfades, and HTML/SVG that the diagram-design language
drops straight into. The Pillow pipeline (see the rest of this skill) is the
zero-dependency fallback; this is the higher-fidelity engine.

## Use it
```bash
cp -r <this template> my-explainer && cd my-explainer
npm install                                  # Remotion + bundled browser, ~free
npx remotion studio                          # live preview while you edit specs
npx remotion render src/index.ts ExplainerWorking out/explainer.mp4   # full video (default: no outro)
npx remotion render src/index.ts scan out/scan.mp4                    # one section
npx remotion still src/index.ts scan out/scan.png --frame=1800 --scale=0.5   # QA still (cheap)
```
The example's narration, bookend audio, and logos ship in `public/`, so the render
commands above work out of the box (asset licensing: repo `NOTICE.md`).

Compositions: `ExplainerWorking` (IntroA + sections, the default shape for new
videos), `Explainer` (same plus the branded outro), one per section id, `Spof`, and
the bookends. `DemoIntro` is the official intro for terminal demos (dark terminal
background); the toolkit ships it pre-rendered as `assets/trustabl-intro.mp4`.

**4K delivery:** `--scale=1.5 --crf=10 --concurrency=2` (renders the 2560x1440 canvas
at 3840x2160). Keep concurrency at 2 on Windows: higher values crash ffmpeg at DLL
init. A 4K60 render runs ~30 min for ~4 min of video, so start it in the background.
QA with stills first, then render once.

**Skins:** navy is the default. `REMOTION_SKIN=light` selects the original light
skin (same token names in `src/brand.ts`); anything else throws.

## Author your video
1. Write the script in `narration.json` (one entry per section, blank lines between
   paragraphs), following the toolkit's `references/14-narration-voice.md`: short
   sentences, contractions, one list at most, and name each thing just before it appears.
2. Voice it: `python <toolkit>/scripts/voice.py .` lints the script, voices every sentence
   (engine and voice from `narration.json`'s `tts`, else the brand profile), writes
   `public/audio/*.mp3`, and writes `src/narration.gen.ts` with each section's exact
   duration and sentence start times. Re-run it after any edit; unchanged sentences come
   from the cache. `--only scan,opa` re-voices just those sections.
3. Edit `src/specs.tsx`, one `Spec` per section. `audioDur: NARRATION.<id>.dur` sets the
   section length. Tie reveals to what's being said with `cue(id, n, frac)` (the start of
   sentence n, plus a fraction of it): `focalAt: cue('contract', 0, 0.75)` for the focal
   group, `atSec: cue('scan', 5)` for any other group. Groups without one spread out
   evenly and finish by ~80% of the voiceover. Never type a duration by hand.
4. Put logos in `public/logos/<name>.png`. Brand colors/fonts live in `src/brand.ts`.
   No em dashes in on-screen text.
5. `Root.tsx` registers each section plus the `Explainer` / `ExplainerWorking` chains
   (slide between sections, fade only at the bookend edges).

## Network primitives
`src/network.tsx` holds the stateful diagram language for network/topology
explainers: `FlowEdge` (curved bezier edge with particles riding it), `RingNode` /
`AppNode` (flip `live → down` on a timeline), `StatCard`, `TagPill`, `CaptionPill`
(timed subtitle beats). These take state timelines in **seconds from the enclosing
Sequence start**, so nodes can fail or re-route mid-scene on the narration beat —
reveals are for *appearing*, states for *changing*. `src/Spof.tsx` (`Spof`,
standard 16:9 canvas) is the worked example: three slides joined by slide/fade
`TransitionSeries`, beats pinned to the narration clips in `public/audio/`:
```bash
npx remotion render src/index.ts Spof out/spof.mp4
```
(`VHeader` in network.tsx is a centered two-tone header for 9:16 vertical cuts,
should a social format ever be needed.)

## Brand
Edit `src/brand.ts` (navy/teal Trustabl defaults). Map the diagram-design roles
(paper→card, ink→text, accent→one focal color) to your palette. Fonts in
`public/fonts/` (Geist + Instrument Serif, swap if your brand differs but keep the
serif title for contrast).

## Credits & licensing
- **Diagram design language**: [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design) (MIT) — typography + node-treatment system.
- **Remotion engine pattern** inspired by [digitalsamba/claude-code-video-toolkit](https://github.com/digitalsamba/claude-code-video-toolkit) (MIT).
- **Remotion** itself is **source-available, not free for all**: free for individuals,
  non-profits, and for-profit companies with **≤3 employees**; larger companies need a
  paid Company License (~$75/mo, remotion.pro). Confirm eligibility before commercial use.
- Fonts: Geist (Vercel, OFL) + Instrument Serif (OFL). Vendor logos are the trademarks
  of their owners — show illustratively, prefer text for ISO/AICPA/PCI/EU marks.
