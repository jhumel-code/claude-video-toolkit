---
name: video-toolkit
description: >
  This skill should be used when the user wants to produce marketing or demo videos
  from the command line — "make a brand intro", "create an animated banner", "record
  a terminal/CLI demo", "make a demo video", "narrate a screencast", "record a Claude
  Code session", or "finish/color-grade a rendered video". A free, deterministic
  Pillow + ffmpeg + VHS + edge-tts pipeline. Brand-agnostic via JSON brand profiles
  (Trustabl ships as the example).
metadata:
  version: "0.1.0"
---

# Claude Video Toolkit

Produce, fully from the CLI and deterministically (no paid tools): brand intros +
looping banners (Pillow/numpy + ffmpeg), narrated terminal demos (VHS + ffmpeg +
edge-tts), and recorded Claude Code sessions. Brand identity is **data** — a profile
in `profiles/<name>.json`.

Paths below are relative to this skill's directory. Read the matching guide in
`references/` before running a workflow; run the tools in `scripts/`.

## Prerequisites — check first, fail loudly if missing
- **VHS recording requires WSL** (Ubuntu) with `vhs` + `ttyd` + chromium libs, run as
  a non-root `demo` user. Windows VHS hangs. Brand intros/banners and finishing do
  NOT need VHS.
- **Host:** `ffmpeg` + `ffprobe`; Python 3 with `pip install edge-tts pillow numpy`;
  optional `sox` for `sound_pads.sh`.
- If a required tool is absent, tell the user exactly what to install before running.

## Brand profiles — the reusable core
- Select a brand with `BRAND_PROFILE=<name>` (default `trustabl`). Profiles live in
  `profiles/`; `example-northwind.json` is a second brand that proves genericity.
- A profile carries: `wordmark`, `tagline`, `pills[]`, `palette` (accent / accent_hi /
  bg_deep / bg_lift / text / subtext), `logo`, `fonts_dir` + `font_family`, a `grade`
  block, `voice`, and a `pronounce` map.
- Add a brand: copy `example-northwind.json`, edit values, drop the logo in `assets/`,
  point `logo` / `font_family` at it. Full schema: `references/11-brand-profiles.md`.
- Inspect: `python scripts/brand_config.py show <profile>` and `... grade <profile>`.

## Golden rules (non-negotiable)
1. **VHS only in WSL**, as `demo`, with absolute `/home/demo/demo/` paths (never `~`);
   a tape's `Output` must be relative.
2. **Narrate with an English-locked voice** (the profile's `voice`, e.g.
   `en-US-AvaNeural`); never a `*MultilingualNeural` voice — they code-switch on coined
   words. The model is the cause; respelling text won't fix it.
3. **You cannot hear audio** — verify by clip durations + `silencedetect`; the human is
   the ear for tone/pronunciation.
4. **Verify frames by eye** (`ffmpeg -ss N -i v.mp4 -frames:v 1 f.png`); vision is
   unreliable on near-identical terminal frames.
5. **Determinism**: edge-tts is byte-stable; live VHS timing is not — re-pin beats each
   render and freeze result frames.

## Style (v2)
6. **Match the visual register to the product.** Restraint reads as trust for
   technical/security tools; avoid bloom/particle/lens-flare excess and let real output
   carry the drama. The "restraint budget" is in `references/10-style-guide.md`.
7. **Always run `finish.sh` last** (fixes dark-gradient banding, applies the brand
   grade, adds subtle grain, encodes bit-exact):
   `GRADE="$(python scripts/brand_config.py grade <profile>)" bash scripts/finish.sh in.mp4 out.mp4 brand`
8. **edge-tts has no usable SSML** — only `--rate` / `--pitch` / `--volume`. Respell
   coined words for TTS (the profile's `pronounce` map); keep on-screen text correct;
   insert pauses as ffmpeg silence between clips, not markup.

## Quickstart

### Brand intro + banner (no VHS)
```bash
BRAND_PROFILE=<profile> OUT_DIR=<workdir> python scripts/brand_intro.py intro    # -> intro_silent.mp4
BRAND_PROFILE=<profile> OUT_DIR=<workdir> python scripts/brand_intro.py banner   # -> banner_silent.mp4
python scripts/sound_gen.py                                                      # soundtrack (set paths inside)
ffmpeg -i intro_silent.mp4 -i intro_audio.wav -c:v copy -c:a aac -shortest intro.mp4
GRADE="$(python scripts/brand_config.py grade <profile>)" bash scripts/finish.sh intro.mp4 intro_final.mp4 brand
```
It renders ~160 supersampled frames — if a single run is too long, render in chunks
(resume by skipping existing frames) and verify frames by eye. Detail:
`references/04-brand-intro-and-banner.md`; sound in `references/05-sound-design.md` and
`scripts/sound_pads.sh`.

### Terminal demo (VHS in WSL)
1. Put commands in a batch JSON (`templates/batch.example.json`), then
   `python scripts/gentape.py batch.json` → `.tape` files. Or copy `templates/branded.tape`.
2. Record in WSL (quoted heredoc — `wsl.exe` mangles `$`):
   ```bash
   wsl.exe -u demo bash -s <<'EOF'
   cd /home/demo/demo && vhs tour.tape
   EOF
   ```
3. Re-pin beats (timing is non-deterministic), fill a `spec.json`
   (`templates/spec.example.json`), then `python scripts/vid.py spec.json` to narrate +
   finish. Detail: `references/02-terminal-demo-factory.md`.

### Record a real Claude Code session
VHS drives `claude` in WSL; `session_vid.py` re-paces the take. Detail:
`references/03-recording-claude-sessions.md`.

## Verification discipline
**After every render, run `scripts/review.sh <render.mp4>` and gate on its exit code (0 PASS,
1 FAIL, 2 no-sidecar) before declaring the video done.** It self-reviews the render WITHOUT a
human: narration-to-visual sync, spillover/double-voice, dead air, loudness/clipping, and
on-screen text (Tesseract OCR), all keyed off the `<name>.beats.json` sidecar the builders
(`vid.py`/`session_vid.py`) emit. On PASS it prints one line; on FAIL, one line per failing
beat. This catches the bugs frame-grabbing misses (audio drifting from its visual, a narration
spilling onto the next section). Builders also apply `profiles/pronounce.json` to narration
before edge-tts to fix jargon pronunciation (edge-tts has no phoneme control). A `pron_suspect`
NOTE still warrants a ~5s human spot-listen - ASR cannot truly hear pronunciation. One-time WSL
setup and full detail: `references/12-self-review.md`. Run `finish.sh` last, and only after
`review.sh` passes on the body.

## References
`references/`: 01 pipeline · 02 terminal-demo-factory · 03 recording-claude-sessions ·
04 brand-intro-and-banner · 05 sound-design · 06 voice-models · 07 environment-and-gotchas ·
08 research-report · 09 improvement-plan · 10 style-guide · 11 brand-profiles ·
12 self-review · brand.md.
