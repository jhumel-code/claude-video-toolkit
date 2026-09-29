# 01 · Pipeline Overview

How the tools fit together. Four production paths share one toolchain.

## Toolchain

| Tool | Role | Where it runs |
|------|------|---------------|
| **VHS** (charmbracelet) | records a terminal session from a `.tape` script to MP4 | **WSL only** (Windows hangs) |
| **edge-tts** | free Microsoft neural TTS, no API key | Windows or WSL |
| **ffmpeg / ffprobe** | all post: concat, mix, freeze, pad, analysis | Windows or WSL |
| **Python 3** (Pillow, numpy) | builders, beat pinner, brand-intro frame generator | Windows or WSL |
| **faster-whisper + tesseract** | the self-review pass (`review.sh`) | WSL |
| **Remotion** (Node) | animated diagram explainers | Windows |

## The four production paths

```
A) TERMINAL DEMO  (real CLI output)
   batch.json ─gentape.py→ *.tape ─VHS(WSL)→ footage.mp4 ─beats.py→ pins
   spec.json ─vid.py→ body.mp4 ─review.sh→ ─assemble.py (+ official intro)→ ─finish.sh demo→ final

B) REAL CLAUDE CODE SESSION  (interactive, non-deterministic)
   tape drives `claude` in WSL ─VHS→ full.mp4 (one long take)
   scenes spec ─session_vid.py→ re-paced narrated cut ─review.sh→ assemble → finish

C) EXPLAINER  (animated diagrams, Remotion)
   specs.tsx + narration mp3s ─remotion render→ explainer.mp4 (IntroA bookend built in)

D) BRAND INTRO / BANNER  (brands without an official intro)
   brand_intro.py → frames → MP4 + sound_gen.py → audio → mux ─finish.sh brand→
```

## House style

- **Canvas 2560x1440, 25 fps** for terminal work, H.264 yuv420p, AAC 48 kHz. Remotion
  explainers render the same canvas at 60 fps, x1.5 for 4K delivery.
- **Terminal:** recorded natively at the canvas size with the brand's theme and margin
  colour (the profile's `terminal` block; gentape.py applies it). Footage that matches
  the canvas is never scaled; other sizes are padded, or scaled down to fit.
- **Voice:** the profile's `tts` block (Trustabl: Kokoro `af_heart`, speed 0.93; see
  `14-narration-voice.md`), coined words respelled through the pronounce map.
- **Loudness:** `loudnorm I=-17` for narration, `I=-15` for a music-bed intro.
- **Bookends:** a brand with an official intro (`intro_clip`) always opens with it;
  terminal demos have no outro.
- **Finish:** `demo` mode (deband only) for recorded footage, `brand` mode for motion
  graphics.

## Core ffmpeg recipes (load-bearing)

- **Concat same-codec**: `-f concat -safe 0 -i list.txt -c copy out.mp4`. Every segment
  must share codec, size, fps, pix_fmt and sar, or it stutters.
- **Freeze / hold a frame**: `tpad=stop_mode=clone:stop_duration=N`. Limit the source
  with `-ss`/`-t` **before `-i`**: `-t` after `-i` is an output limit that truncates the
  freeze (the clip ends short by exactly the freeze length). Input seeking with a
  re-encode is frame-accurate, even on VHS footage with keyframes 10 s apart.
- **Fit to canvas without distortion**: native size: nothing; otherwise
  `scale=W:H:force_original_aspect_ratio=decrease:flags=lanczos,pad=W:H:(ow-iw)/2:(oh-ih)/2:color=0x070E1A`.
- **Mix narration onto silent video**: per clip `[i:a]adelay=<ms>:all=1` →
  `amix=inputs=N:duration=longest:normalize=0` → `loudnorm=I=-17:TP=-2:LRA=11`, then
  mux with `-c:v copy` so the picture is not re-encoded again.
- **Pitch-preserving tempo fit**: `atempo=1.0..1.3` to fit a too-long clip into a slot.
- **Frame extract (verify)**: `-ss T -i v.mp4 -frames:v 1 f.png`; the true last frame
  `-sseof -0.1`.
- **Structure analysis**: `silencedetect=noise=-38dB:d=0.4` for narration gaps and
  overlaps; `scripts/beats.py` for where terminal output lands.
- **Ken Burns on a static hold** (legacy look, optional): `zoompan=z='min(1.0+rate*on,1.03)':d=1:x=0:y=0`.
  Anchor `x=0` on left-aligned text (a centre anchor slides sideways) and never zoom
  dense scrolling output: it clips the content the narration references.
