# 01 · Pipeline Overview

How the tools fit together. Three production paths share one toolchain.

## Toolchain

| Tool | Role | Where it runs |
|------|------|---------------|
| **VHS** (charmbracelet) | records a terminal session from a `.tape` script → MP4 | **WSL only** (Windows hangs) |
| **edge-tts** | free Microsoft neural TTS, no API key | Windows |
| **ffmpeg / ffprobe** | all post: concat, mix, freeze, zoom, upscale, tempo-fit, analysis | Windows |
| **Python 3** (Pillow, numpy) | orchestration + the brand-intro frame generator | Windows |
| **Bash** (git-bash / WSL) | the make/mix shell glue | both |

## The three production paths

```
A) TERMINAL FEATURE DEMO  (deterministic CLI output)
   batch.json ─gentape.py→ *.tape ─VHS(WSL)→ footage.mp4
                 spec.json ─vid.py→ narrated, upscaled, zoomed MP4   ← finished

B) REAL CLAUDE CODE SESSION  (interactive, non-deterministic)
   tape drives `claude` in WSL ─VHS→ full.mp4 (one long take)
                 spec ─session_vid.py→ re-paced narrated cut          ← finished

C) BRAND INTRO / BANNER  (motion graphics, no terminal)
   brand_intro.py → frames → MP4   +   sound_gen.py → audio → mux     ← finished
```

## Core ffmpeg recipes (load-bearing)

- **Concat same-codec**: `-f concat -safe 0 -i list.txt -c copy out.mp4`
  (re-encode all segments to identical CRF/preset/pix_fmt/fps/sar first, or it stutters).
- **Freeze / hold a frame**: `tpad=stop_mode=clone:stop_duration=N`.
  Limit the source with `-ss`/`-t` **BEFORE `-i`** — `-t` AFTER `-i` is an output
  limit that *truncates the freeze* (silent bug: clip ends short by the freeze length).
- **Mix narration onto silent video**: per clip `[i:a]adelay=<ms>:all=1[ai]` →
  `amix=inputs=N:duration=longest:normalize=0` → `loudnorm=I=-17:TP=-2:LRA=11`.
- **Quality upscale** (the house look): `scale=2600:1680:flags=lanczos,
  unsharp=3:3:0.4:3:3:0.0` then output **1950x1260** (1.5× of VHS's 1300×840), CRF 16.
- **Ken Burns zoom on terminal text**: `zoompan=z='min(1.0+rate*on,1.03)':d=1:x=0:y=0:
  s=1950x1260:fps=25` where `rate=(cap-1)/total_frames`. **LEFT-ANCHOR x=0** — a
  center-anchored zoom on left-aligned text drifts toward the corner ("sideways
  sliding"). Zoom only **sparse/static** beats; never zoom dense scrolling output
  (it clips the content the narration references).
- **Pitch-preserving tempo fit**: `atempo=1.0..1.3` to fit a too-long clip into its slot.
- **Frame extract (verify)**: `-ss T -frames:v 1 f.png`; true last frame `-sseof -1`.
- **Structure analysis**: `silencedetect=noise=-38dB:d=0.4` (narration gaps/overlaps),
  `freezedetect=n=-50dB:d=0.8` (static-segment boundaries = where output prints/holds).

## House style (consistency across all videos)

- Output **1950×1260**, 25 fps, CRF 16, yuv420p, AAC 192k.
- Terminal: VHS **Dracula** theme, **FontSize 14**, **1300×840**, Padding 16,
  TypingSpeed ~32-35ms.
- Voice: **en-US-AvaNeural**, natural rate (no `--rate`).
- Loudness: `loudnorm I=-17` for narration videos, `I=-15` for the intro (music bed).
