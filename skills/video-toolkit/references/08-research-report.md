# Elevating the Trustabl Video Toolkit — Research Report

_Scope: how professional, AI-assisted product-marketing video maps onto a **free, CLI-first, deterministic** pipeline (Pillow/numpy + ffmpeg + VHS + edge-tts). No paid SaaS, no generative-AI video/voice._

_Method: five parallel research agents (motion-design craft, ffmpeg finishing, dev-tool video genre, terminal-demo elevation, AI-as-director + free sound), each grounded in cited sources. Consolidated sources at the end._

---

## The headline insight: precision over spectacle

The most important finding cuts against the current direction of our intro. Two research tracks gave opposite advice, and resolving that tension is the spine of everything below.

The motion-craft track says premium films use bloom, glow, particle fields, film grain, and chromatic aberration. The dev-tool/security-genre track says the opposite for our category: _"particle explosions, lens flare, and bloom read as consumer/game marketing. Security tools must signal calm authority, not excitement. Restraint **is** the signal — let a critical finding carry its own weight."_ The genre leaders for serious/technical tools (Linear, Stripe, Snyk/Semgrep-style demo-first positioning) win by being quiet, evidence-first, and clinical.

Our current `brand_intro.py` is glow-, bloom-, and particle-heavy — visually closer to a consumer app launch than to a static-analysis tool. **This is the recalibration to make:** keep the craft techniques that read as *competence* (easing, kinetic type, parallax, clean grade, banding-free backgrounds, smooth zoom, captions) and spend the "spectacle budget" sparingly — a single restrained glow on the shield, no sustained chromatic aberration, a thinner particle field. The drama should come from real `trustabl` output (real rule IDs, real file paths, real scores), not from effects.

This isn't "less effort" — it's *aimed* effort. Quiet and precise is harder to do well than loud, and it's what makes a security tool look trustworthy.

---

## 1. Motion craft that reads as premium (and is reproducible deterministically)

**Easing is the cheapest, highest-impact upgrade.** Linear motion and the default quad/sine curves read as "cheap." Cubic / quint / expo curves read as "premium" because the acceleration contrast makes elements feel like they have mass. Use ease-out for entrances (arrive fast, settle gently), ease-in-out for moves, ease-in for exits, and a small ease-out-back overshoot (+5–8%) for spring energy. Concrete formulas and per-element durations are in the style guide.

**Kinetic typography** separates amateur from editorial. The three premium reveal classes, all doable in Pillow: a left-to-right **mask/clip wipe** (text exists fully formed; the mask moves — zero aliasing loss), **per-letter stagger** (8 px translate-up + alpha, 4–6 frame offset between letters), and **blur-in** (GaussianBlur→sharp over ~18 frames) for taglines. A simultaneous fade — what we do now — is the weakest option.

**Depth & parallax** give a flat composition dimension cheaply: assign each layer a depth factor `d∈[0,1]`, and on a slow 4% push-in, move/scale each layer by `d`. Background particles drift at ~20% of the logo's rate. This is pure compositing in the existing frame loop.

**Frame rate & motion blur:** 30fps is the right default (clean from a Pillow sequence; crisper than 24 for terminal/code content, without the "video" feel of 60). Add motion blur only on fast moves (the shield entrance) by averaging 3 sub-frame renders — deterministic, and invisible-but-felt. Skip it on text and particles (it hurts legibility).

## 2. ffmpeg as a finishing/compositing engine

**Fix the dark-gradient banding first — this is a real defect in the current intro.** Deep navy `#00090F→#01242B` spans <~28 luma steps; in yuv420p H.264 those collapse into visible bands. Three stacking fixes: add a faint noise floor before encode, run `deband`, and carry the intermediate in 10-bit (`yuv444p10le`) converting to `yuv420p` only at final encode. (Use `deband`, **not** `gradfun`, in a mastering chain — `gradfun` is documented as playback-only.)

**A subtle color grade** unifies the palette: lift shadows slightly toward teal, cool the mids, roll highlights toward the brand off-white, desaturate ~8% for a matte-premium finish (exact `curves`/`eq`/`colorbalance` values in the style guide).

**Smooth zoom** (for the demo) requires supersampling: pre-scale to ~4× with lanczos *before* `zoompan`, then downscale — this is the difference between studio-grade motion and pixel stair-stepping. Anchor `x=0` on terminal text so columns don't drift.

**Determinism is achievable** but x264 is only bit-reproducible single-threaded: `-threads 1 -fflags +bitexact -x264-params threads=1:sliced-threads=0`. Avoid `minterpolate` (non-deterministic across thread counts); `tmix` is the deterministic motion-blur path.

## 3. The dev-tool video genre — what to emulate

The dominant aesthetic is "Linear-style dark premium": cool near-black backgrounds (not pure `#000`), high-contrast type, one restrained accent, real product UI over decoration. Every high-performing dev-tool video follows a **five-beat arc**: hook (≤5s) → problem → product reveal → live proof/demo → CTA — and gets to value in the first 3–5 seconds.

**Length targets:** brand intro/sting **10–15s** (1–2 motion beats, no scene cuts, no voice); product demo **90–120s** (full feature tour up to ~3 min). **Captions are load-bearing** — most dev video is watched muted — but use static-line swaps, *not* TikTok-style word karaoke (which reads as consumer).

**For a security tool specifically, "premium + trustworthy" means:** restraint over flash; evidence before claims (show real output before any voiceover assertion); color encodes *severity* not branding (red/amber findings on near-black look like a real CI dashboard); fast scan completion is itself a trust signal; tight typography as a proxy for analytical precision; and **no hype words** in captions ("blazing-fast," "powerful," "seamless" read as noise — describe what's happening instead).

## 4. Terminal-demo elevation (deterministic)

**Output MP4 from VHS, never GIF** (GIF's 256-color limit makes themes grainy and files larger). VHS remains the right recorder for us (deterministic, headless-WSL, MP4). Elevate the capture with a **custom branded VHS theme** (navy bg + teal accent), a `WindowBar` + `BorderRadius` + `MarginFill` for a framed-window look, JetBrainsMono Nerd Font at large size, recorded at 2× and downscaled.

**Demo cadence is a real technique:** type at natural speed (~35 ms/char), then `PlaybackSpeed 2.0` through the boring scan-progress phase, drop back to `1.0` and hold ~4s on the findings. Boring parts accelerated, payoff held — this is exactly how `bun`/`uv` demos feel fast.

**Post-production callouts** (all timed, deterministic, free): zoom-to-region (left-anchored), a teal highlight box around the key finding line (`drawbox` fill + border, `enable='between(t,...)'`), spotlight-dimming of non-focus rows (split → darken → overlay), and lower-third labels via **ASS** (libass is far more stable than `drawtext` on Windows). Render terminal text with Pillow only for *supplementary* graphics (badges, score cards) — never to fake the whole terminal, which destroys authenticity for a live-scan demo.

## 5. AI as director + free voice/sound

**The unifying architecture:** an LLM acts as *director*, emitting a `spec.json` (scenes, narration, timings, beds, captions); the deterministic Python/ffmpeg pipeline *renders* it. This turns each bespoke video into a data-driven render and is the cleanest way to make intro + demo "one system." A schema is in the style guide.

**edge-tts reality check (verified):** Microsoft blocks custom SSML — only `--rate`, `--pitch`, `--volume` work. No `<break>`, `<emphasis>`, `<say-as>`, or `<phoneme>`. Consequences: insert pauses as **ffmpeg silence between clips**, not in TTS; and pronounce coined words like **"Trustabl" by respelling the input text** (verified: "Trustable" reads naturally; "Trust-abl" makes AvaNeural spell out A-B-L — the human is the ear). Use `--write-subtitles` to get word-boundary timings for free, accurate captions.

**Richer free, deterministic sound** beyond our current sine chords: stack harmonics through `aevalsrc` + `lowpass` with attack/release envelopes for warm pads; use SoX's `pl` (Karplus-Strong plucked-string) for natural risers and UI blips; and Csound for programmable chord progressions generated from the spec. All are CLI-scriptable and byte-deterministic.

---

## What this means for us

Three actions, in order of leverage: (1) **recalibrate the aesthetic** toward restraint/evidence for the security category; (2) **fix the two defects** (gradient banding; edge-tts pronunciation/pacing handling); (3) **upgrade the craft** (easing, kinetic type, parallax, grade, smooth zoom, branded terminal, ASS captions, richer sound) and unify it behind a `spec.json`-driven renderer. The concrete, prioritized changes are in **09-improvement-plan.md**; the reusable parameters in **10-style-guide.md**.

---

## Sources

**Motion design & timing:** Disney's 12 Principles in UI (medium.com/design-bootcamp); easings.net; SVGator easing guide; Apple HIG — Motion; Number Analytics / IKA Agency kinetic typography; 180-degree shutter rule (DIYPhotography); teal-orange grading (PetaPixel).

**ffmpeg technique:** ffmpeg.org filter docs; Ken Burns with ffmpeg (mko.re); smooth zoompan no-jiggle (datarecoveryunion.com); ultimate film grain gist (logiclrd); retro glow / vintage filters (zayne.io); LUT/hald-CLUT grading (gabor.heja.hu); xfade (OTTVerse); xfade-easing (scriptituk/GitHub); scaling quality (Streaming Learning Center); banding fixes (VideoHelp forum); deterministic transcoding (livepeer/research); Windows fontconfig fix (pureandapplied.com.au).

**Dev-tool video genre:** Linear design trend + UI redesign (LogRocket; linear.app/now); dev-tool launch weeks — Resend/Linear/Supabase (daily.dev); product-demo best practices (What a Story; Gartner Digital Markets); tasteful screen recording (Clueso); caption styling (3Play Media); Vercel hero analysis (hero.gallery); Warp 2024 review.

**Terminal recording:** charmbracelet/vhs README; VHS scripted recordings (rdiachenko.com); VHS use cases (tywer.dev); asciinema agg docs; awesome-terminal-recorder; ffmpeg zoom (OSTechNix); silicon; rich (Textualize).

**AI-director, voice & sound:** rany2/edge-tts README + issue #58 + PyPI; Edge TTS guide (VideoSDK); aevalsrc examples (hhsprings); sox chords (scruss.com); CsoundAC (Linux Journal); hook-body-CTA frameworks (Sovran; Virvid); AI video via JSON + Remotion (Medium).
