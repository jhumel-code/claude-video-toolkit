# Remotion animated diagram explainer (template)

> **Codename: Slipstream (v2) — the default template.** Versions are git-tagged:
> `template/slipstream-v2` (this one; stateful network primitives, slide-deck Spof
> example, two-tone headers) and `template/harbor-v1` (its reveal-only predecessor).

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
npx remotion render src/index.ts Explainer out/explainer.mp4   # full video
npx remotion render src/index.ts scan out/scan.mp4             # one section
```

## Author your video
1. Put narration mp3s in `public/audio/sy_<id>.mp3` (e.g. from this skill's
   `make_voice.sh` / edge-tts). Measure each duration.
2. Edit `src/specs.tsx` — one `Spec` per section: `eyebrow`, `title`, `logo`,
   `audio`, `audioDur` (seconds), and ordered `groups[]` (each a reveal step holding
   `nodes` / `arrows` / `pills` / `mono`). Reveals auto-pace across `audioDur` and
   finish by ~80% so nothing pops in at the cut.
3. Put logos in `public/logos/<name>.png`. Brand colors/fonts live in `src/brand.ts`.
4. `Root.tsx` registers each section + the master `Explainer` (crossfade chain).

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
