# Trustabl Video Toolkit — Prioritized Improvement Plan

Each item: **what · why · file · how (recipe) · effort · impact.** Effort/impact are S/M/L.
Tiers: **P1** = do first (high impact, low effort, or fixes a defect). **P2** = high impact, moderate effort. **P3** = system-level, larger.

Everything here stays free, CLI, and deterministic.

---

## P1 — Do first

### 1. Fix dark-gradient banding (defect)
- **Why:** the navy radial bg (`#00090F→#01242B`) bands visibly in yuv420p — present in the intro/banner shipped today.
- **File:** `brand_intro.py` (final ffmpeg encode) + a new finishing pass.
- **How:** carry frames at higher precision and deband+dither at encode:
  ```bash
  ffmpeg -v error -y -framerate 30 -i bi_intro/f%04d.png \
    -vf "deband=thr=0.025:range=12:blur=true,noise=alls=5:allf=u,format=yuv420p" \
    -c:v libx264 -crf 16 -preset slow -pix_fmt yuv420p intro_silent.mp4
  ```
  For maximum smoothness, render the PNGs themselves with a 1-LSB ordered dither on the gradient in numpy (add `np.random.default_rng(SEED).integers(0,2,size)` — seeded = deterministic) before quantizing to uint8.
- **Effort:** S · **Impact:** L

### 2. Recalibrate the aesthetic toward restraint (security-tool positioning)
- **Why:** bloom/particles/aberration read as consumer/game; a static-analysis tool should read calm, precise, clinical. Biggest *strategic* change.
- **File:** `brand_intro.py`.
- **How (specific edits):**
  - Cut the particle count ~60% (`range(80)` → `range(30)`), lower brightness, slow the twinkle.
  - Remove the seal-flash bloom *or* drop its strength to ≤0.3 and shrink radius; keep **one** soft inner glow on the shield only.
  - Do **not** add sustained chromatic aberration (if used at all, only the first ~4 frames).
  - Let the wordmark + tagline + one accent be the focus; more negative space.
- **Effort:** S–M · **Impact:** L (this is the difference between "app launch" and "security tool")

### 3. Final color-grade pass (palette cohesion)
- **Why:** unifies everything to the teal/navy brand, adds matte-premium feel.
- **File:** new `finish.sh` (or fold into `vid.py` / `brand_intro.py` encode).
- **How:**
  ```bash
  -vf "curves=r='0/0 0.5/0.48 1/1':g='0/0 0.5/0.51 1/1':b='0/0 0.5/0.56 1/1',\
       eq=contrast=1.06:brightness=-0.02:saturation=0.92,\
       colorbalance=bs=0.05:bh=0.03"
  ```
- **Effort:** S · **Impact:** M

### 4. Subtle grain + vignette finishing layer
- **Why:** texture reads as "shot, not generated," and grain *also* mitigates banding.
- **File:** `finish.sh`.
- **How:** `-vf "noise=c0s=18:c0f=t+u, vignette=PI/5"` (luma-only grain ≤22; vignette `PI/5` subtle). Keep both subtle — restraint.
- **Effort:** S · **Impact:** M

### 5. Premium easing defaults
- **Why:** current `e_out` is cubic (fine); quint/expo entrances feel more "weighted/premium."
- **File:** `brand_intro.py` easing helpers.
- **How:** add and use `ease_out_quint = 1-(1-t)**5` for entrances, `ease_in_out_cubic` for moves, `ease_out_back` for one tasteful overshoot on the shield settle.
- **Effort:** S · **Impact:** M

---

## P2 — High impact, moderate effort

### 6. Kinetic typography (wordmark + tagline)
- **Why:** simultaneous fade-in is the weakest reveal; editorial reveals signal quality.
- **File:** `brand_intro.py` wordmark/tagline render.
- **How:** wordmark = left-to-right **mask wipe** (render "Trustabl" once, reveal via an expanding clip mask over ~18 frames). Tagline = **per-word stagger** (word i starts at frame `i*6`, each ease-out-quint over ~14 frames, 8 px translate-up + alpha). Pills (if kept) cascade with 4–6 frame offsets — already close.
- **Effort:** M · **Impact:** L

### 7. Depth & parallax push-in
- **Why:** turns a flat 2D composition into something with dimension; "breathes forward."
- **File:** `brand_intro.py` frame loop.
- **How:** assign layers depth `d` (particles 0.2, chevrons 0.3, shield 0.6, wordmark 0.8, tagline 1.0). Apply a 4% push over the clip: scale layer by `1 + 0.04*d*t`; optional idle drift `x = 12*d*sin(2πt)`. Composite back to canvas size.
- **Effort:** M · **Impact:** M–L

### 8. Branded terminal capture + demo cadence (demo)
- **Why:** the demo currently uses a generic Dracula theme at small size, constant speed. A branded, framed terminal with accelerated boring parts is the genre standard.
- **File:** `gentape.py` HEAD / the `.tape` template.
- **How:** custom VHS theme (navy bg, teal accent), `Set WindowBar Colorful`, `Set BorderRadius 10`, `Set Margin 40`, `Set MarginFill "#070E1A"`, `JetBrainsMono Nerd Font`, `FontSize 36`, `Framerate 30`, `CursorBlink false`. Cadence: type at 35ms, then `Set PlaybackSpeed 2.0` through scan progress, `1.0` and hold ~4s on findings. Full theme JSON in the style guide.
- **Effort:** M · **Impact:** L

### 9. Demo post-production: zoom, callouts, spotlight, captions
- **Why:** directs the eye to the finding that matters; captions serve muted viewers.
- **File:** `vid.py` (extend) or a new `demo_post.sh`.
- **How (timed, deterministic):**
  ```bash
  # left-anchored zoom into the findings region (supersample first!)
  scale=7680:4320:flags=lanczos,
  zoompan=z='if(between(t,12,18),min(zoom+0.0010,1.35),1)':d=1:x=0:y=320:fps=30:s=1920x1080,
  # teal highlight box on the key line (fill + border, timed)
  drawbox=x=40:y=480:w=2200:h=52:color=0x51C1B5@0.30:t=fill:enable='between(t,13,17)',
  drawbox=x=40:y=480:w=2200:h=52:color=0x51C1B5:t=2:enable='between(t,13,17)',
  ass=captions.ass
  ```
  Pin the `y` by extracting the findings frame first (`ffmpeg -ss 12 -i tour.mp4 -frames:v 1 f.png`).
- **Effort:** M · **Impact:** L

### 10. edge-tts pronunciation, pacing & free captions
- **Why:** SSML is blocked; "Trustabl" mispronounces; pauses can't be authored in TTS. Fix at the pipeline level.
- **File:** `vid.py` / narration step.
- **How:** respell coined words in the TTS input only ("Trust-abl" — keep on-screen text correct); add pauses as ffmpeg silence between clips (`aevalsrc=0:d=0.4`); per-emphasis line, render that clip with `--rate=-10% --pitch=-6Hz`; generate captions from `edge-tts --write-subtitles` word boundaries → ASS.
- **Effort:** M · **Impact:** M

---

## P3 — System-level

### 11. `spec.json`-driven renderer (make intro + demo one system)
- **Why:** unifies bespoke videos into a data-driven pipeline; lets an LLM act as director while rendering stays deterministic.
- **File:** new `render_spec.py` orchestrating `brand_intro.py`, VHS, `vid.py`, sound.
- **How:** define the schema (see style guide §7); `render_spec.py` walks `scenes[]`, renders each (title_card / terminal_replay / findings_card / cta_card), synthesizes `audio_beds`, runs edge-tts per scene, concatenates with `xfade`, applies `finish.sh`. One spec → one byte-stable video.
- **Effort:** L · **Impact:** L

### 12. Richer deterministic sound design
- **Why:** the current sine-chord bed is thin; pads/risers/blips with envelopes feel composed.
- **File:** `sound_gen.py` (extend) + optional `sound/` recipes.
- **How:** warm pads via stacked harmonics + envelope:
  ```bash
  ffmpeg -f lavfi -i "aevalsrc='0.07*(sin(2*PI*110*t)+sin(2*PI*164.81*t)+sin(2*PI*220*t)+sin(2*PI*261.63*t))*(1-exp(-t/0.4))*exp(-max(t-6,0)/1.5)':d=8:s=48000,lowpass=f=900:poles=2" -ac 2 pad_Am.wav
  ```
  Risers/blips via SoX Karplus-Strong (`sox -n riser.wav synth pl C3 pl E3 ... delay ... remix - fade 0 8 .2 norm -1`); optional Csound for chord progressions. Master at loudnorm I=-15 (bed) / I=-17 (under VO).
- **Effort:** M · **Impact:** M

### 13. Captions + multi-format export as standard
- **Why:** muted viewers; different channels (X/LinkedIn/YouTube/GitHub) need different frames.
- **File:** `finish.sh`.
- **How:** always emit an ASS-captioned 1920×1080 master; add a 1:1 and 9:16 export via `scale=...:force_original_aspect_ratio=decrease,pad=...:color=0x0D1B2A` (navy letterbox). Caption style in style guide §6.
- **Effort:** S–M · **Impact:** M

### 14. Lock determinism
- **Why:** the toolkit's promise is reproducibility; x264 isn't bit-exact multi-threaded.
- **File:** every ffmpeg encode.
- **How:** `-threads 1 -fflags +bitexact -x264-params threads=1:sliced-threads=0`. Seed any numpy RNG. Avoid `minterpolate`. Keep grain via seeded `geq`/`noise` (PTS-seeded = stable).
- **Effort:** S · **Impact:** M (correctness, not looks)

---

## Suggested sequence

1. **Quick-win finishing pass** (items 1, 3, 4, 14) — one new `finish.sh`, re-encode the existing intro/banner. Immediate, visible lift + fixes the banding defect.
2. **Recalibrate + craft the intro** (2, 5, 6, 7) — the restraint pass + kinetic type + parallax.
3. **Elevate the demo** (8, 9, 10) — branded terminal, cadence, callouts, captions.
4. **Systematize** (11, 12, 13) — spec-driven renderer + richer sound + multi-format.

A good proof-of-concept is to re-render the **current** intro through items 1+3+4 only (no creative change) — a pure finishing pass — to show the banding fix + grade + grain delta before investing in the bigger creative work.
