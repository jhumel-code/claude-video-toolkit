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
See `templates/remotion-diagrams/README.md`. In short: drop narration mp3s in
`public/audio/`, edit `src/specs.tsx`, `npx remotion studio` to preview,
`npx remotion render src/index.ts Explainer out/explainer.mp4`.

## Licensing (read before commercial use)
Remotion is **source-available, not free for all**: free for individuals, non-profits,
and for-profit companies with **≤3 employees**; larger companies need a paid Company
License (~$75/mo). The Pillow pipeline remains the $0 fallback. The diagram-design
language and the digitalsamba toolkit it's modeled on are both MIT.
