# Claude Video Toolkit — Motion & Video Style Guide

> Brand-specific values (palette, wordmark, pills, grade, voice) live in the brand
> profile (`profiles/<name>.json`); the principles here are universal. Examples use the
> Trustabl profile. See [11-brand-profiles](11-brand-profiles.md).

The reusable spec future videos conform to. Values are chosen for a **security / static-analysis** tool: calm, precise, evidence-first. The guiding rule is **restraint** — spend effects sparingly; let real output carry the drama.

---

## 1. Motion language

**Easing (normalized t ∈ [0,1]):**
```python
ease_out_quint   = lambda t: 1-(1-t)**5          # entrances (default)
ease_in_out_cubic= lambda t: 4*t**3 if t<.5 else 1-(-2*t+2)**3/2   # moves
ease_out_back    = lambda t: 1+2.70158*(t-1)**3+1.70158*(t-1)**2   # one tasteful overshoot
ease_in_cubic    = lambda t: t**3                # exits
```
Defaults: **ease-out for entrances, ease-in-out for moves, ease-in for exits.** Use `ease_out_back` once (shield settle), never on text.

**Durations @ 30fps:** wordmark reveal 18–24f (0.6–0.8s) · tagline 12–18f · stagger offset 6–8f · pre-outro hold 30–60f · particle/element settle 30–45f. **Anticipation:** 3–5f counter-move before a "slam." **Stagger:** small offsets (4–6f) so cascades read as a ripple.

**Frame rate:** 30fps everywhere. **Motion blur:** only on fast moves (shield entrance) via 3 sub-frame average; never on text/particles.

## 2. Typography

- **Wordmark/titles:** Poppins SemiBold, 48–72px @1080p (2.5–4% of frame height). Tracking −0.01 to −0.02em on display text (signals precision).
- **Body/labels/code:** Inter or JetBrainsMono.
- Max 2 weights on screen at once. No ALL-CAPS for multi-word callouts.

## 3. Color system

| Token | Hex | Use |
|---|---|---|
| Teal (primary accent) | `#51C1B5` | highlights, borders, key data — **≤5–10% of screen area** |
| Teal highlight | `#96EBDC` | the single restrained glow |
| BG deep | `#00090F` | background base (cool near-black) |
| BG lift | `#01242B` | gradient toward motif |
| Terminal BG | `#0D1B2A` | demo terminal background |
| White | `#F7F9F7` | primary text |
| Grey subtext | `#96A6B2` | tagline / secondary |

**Severity colors (findings):** critical `#FF6B6B` · warning `#FFD166` · info `#4EA8DE`. Color encodes *severity, not branding* — this makes output look like a real CI dashboard. Gradients only on **static** backgrounds, never on moving elements.

## 4. Color grade (final pass)
The grade is the brand profile's `grade` block, applied by `finish.sh` in `brand` mode
(`GRADE="$(python scripts/brand_config.py grade <profile>)"`). It must **lift** midtones
(curves above 0.5, positive `eq` brightness), never darken: the June grade here used
`brightness=-0.02` and made every video read dark. Recorded footage (terminal, screen
capture) gets **no** grade: `finish.sh ... demo`.

## 5. Effects "restraint budget"

| Effect | Allowed? | Ceiling |
|---|---|---|
| Banding fix (deband+dither) | **Required** | finish.sh's `deband` (both modes) |
| Film grain (luma) | Motion graphics only | `GRAIN=6` default, `GRAIN=2` for explainers; never on terminal footage |
| Vignette | Motion graphics only | `VIG=PI/16`. The angle runs opposite to intuition: a LARGER angle crushes the corners (`PI/5` darkened a whole 4K render). Test one frame before a full pass. |
| Glow/bloom | Sparingly | one soft glow on the shield only, `gblur sigma≤18`, screen blend opacity ≤0.30 |
| Chromatic aberration | Rarely | first ~4 frames only, `rgbashift` ≤2px; never sustained |
| Particles | Thin | ~30 max, low brightness |
| Lens flare / explosions | **No** | — |

## 6. Captions (ASS)

Style: Poppins SemiBold 28–32px @1080p, bottom-third, white `#F7F9F7`, 2px teal-tinted outline, 50% black shadow/pill, ≤42 chars/line, ≤2 lines, never over the output region. **Static-line swaps only — no word-karaoke.** Lead audio by 0ms. No hype words ("blazing-fast," "powerful," "seamless"); describe what's happening.
```
Style: Default,Poppins,30,&H00F7F9F7,&H000000FF,&H40251C1B,&H80000000,0,0,0,0,100,100,0,0,1,2,1.5,2,40,40,50,1
```
Generate timings from `edge-tts --write-subtitles`.

## 7. Terminal demo spec

The terminal look is the brand profile's `terminal` block (canvas size, font size,
padding, margin and margin colour, window bar, typing speed, theme); `gentape.py` writes
it into every tape and `templates/demo.example.tape` shows the result for Trustabl:
2560x1440 native (the video canvas, so nothing is scaled), FontSize 28, navy
`#0D1B2A` background, `#E8EBF0` text, teal `#51C1B5` cursor, `WindowBar Colorful`,
`Margin 40` on `#070E1A` (the canvas the official intro sits on), `BorderRadius 12`.
The WSL font is DejaVu Sans Mono (no JetBrains font is installed there).
**Cadence:** type at 35 ms, a 2 s pause before Enter, hold 4 s or more on results.
**Zoom:** none on terminal footage; if a static hold ever needs one, anchor `x=0`.

## 8. Sound spec

- **Voice:** the profile's English-locked voice and rate (Trustabl: `en-US-AvaNeural`,
  `--rate=-7%`, one token). Never `*MultilingualNeural`. Pronounce coined words by
  **respelling the TTS input** ("Trustable") through the pronounce map; keep on-screen
  text correct. Pauses are ffmpeg silence between clips, not SSML (only
  rate/pitch/volume work).
- **Music beds:** warm pads via stacked-harmonic `aevalsrc` + `lowpass` + attack/release envelope; risers/blips via SoX `pl`. Bed under VO at −18dB vs voice. No lyrics.
- **Mastering:** music bed `loudnorm I=-15:TP=-1.5`; under-VO bed `I=-17`. Findings reveal = one short confirmation ping (CI-green-check feel).
- **You are the ear:** verify by clip durations + `silencedetect`; human confirms tone.

## 9. Proposed scene-spec schema (not built)

A design for a single `render_spec.py` that would render title cards, terminal replays
and CTA cards from one spec. It does not exist; the working specs are vid.py's
(`templates/spec.example.json`), session_vid.py's, and the Remotion template's
`specs.tsx`.
```json
{
  "video_id": "string", "duration_s": 45, "fps": 30, "resolution": [1920,1080],
  "narration_voice": "en-US-AvaNeural", "narration_rate": "+8%", "narration_pitch": "-3Hz",
  "scenes": [
    {"id":"hook","start_s":0,"end_s":5,"type":"title_card",
     "text":"On-screen text (correct spelling)","narration":"TTS text (respelled)",
     "bg_color":"#00090F","text_color":"#F7F9F7","font_size":52,"audio_bed":"pad_intro","zoom":null},
    {"id":"scan","start_s":18,"end_s":32,"type":"terminal_replay",
     "tape_file":"tapes/scan.tape","narration":"...","highlight_line":7,
     "freeze_frame_s":24.0,"freeze_duration_s":2.0,"audio_bed":"pad_mid"},
    {"id":"proof","type":"findings_card","data":{"rules":183,"sdks":10},"narration":"...","audio_bed":"riser"},
    {"id":"cta","type":"cta_card","text":"trustabl scan .","subtext":"github.com/trustabl/trustabl","narration":"...","audio_bed":"pad_outro"}
  ],
  "audio_beds": {"pad_intro":{"type":"ffmpeg_lavfi","recipe":"Am_pad_8s"},
                 "riser":{"type":"sox","recipe":"glissando_up_8s"}},
  "caption_srt": "captions/<id>.srt"
}
```
Scene types: `title_card`, `terminal_replay`, `findings_card`, `cta_card`.

## 10. Determinism & encode

For Pillow motion graphics: 30fps · render 2× then downscale lanczos · final encode
(`finish.sh`'s default; terminal demos are 25fps at their native canvas):
```bash
-threads 1 -fflags +bitexact -c:v libx264 -x264-params threads=1:sliced-threads=0 \
-preset slow -crf 16 -pix_fmt yuv420p
```
Seed all numpy RNG. Avoid `minterpolate`. Carry intermediates 10-bit (`yuv444p10le`) when banding-prone; convert to `yuv420p` only at final encode.

## Narrative defaults

Five-beat arc: **hook (≤5s) → problem → product → proof → CTA**; value in the first 3–5s. Open on the brand's official intro when it has one (Trustabl: the 4.3 s logo bookend, then straight into the demo; no outro on demos). The opening narration, or an explainer's overview section, must say what the video is for: a logo alone is not an intro. Demo **90–120s** (tour ≤3min). Evidence before claims; show real `trustabl` output before any voiceover assertion. No structural labels ("Act one", "Part 2") in narration.
