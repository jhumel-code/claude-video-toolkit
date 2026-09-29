---
name: video-toolkit
description: >
  This skill should be used when the user wants to produce a marketing, demo, or explainer
  video from the command line: "make a demo video", "record a terminal/CLI demo", "narrate
  a screencast", "record a Claude Code session", "make an explainer video", "make a brand
  intro", "create an animated banner", or "finish/color-grade a rendered video". A free,
  deterministic VHS + edge-tts + ffmpeg pipeline for real terminal footage, a Remotion
  template for animated diagram explainers, and Pillow motion graphics. Brand-agnostic via
  JSON brand profiles (Trustabl ships as the example).
metadata:
  version: "0.2.0"
---

# Claude Video Toolkit

Produce narrated terminal demos (VHS + edge-tts + ffmpeg), animated diagram explainers
(Remotion), recorded Claude Code sessions, and brand intros/banners (Pillow), fully from the
CLI. Brand identity is **data**: a profile in `profiles/<name>.json`.

Paths below are relative to this skill's directory. Read the matching guide in
`references/` before running a workflow; run the tools in `scripts/`.

## Prerequisites: check first, fail loudly if missing
- **Host:** `ffmpeg` + `ffprobe`; Python 3 with `pip install edge-tts pillow numpy`.
- **VHS recording and `review.sh` run in WSL** (Ubuntu) as a non-root `demo` user:
  `vhs` + `ttyd` + chromium libs, `tesseract-ocr`, and `faster-whisper`
  (`references/12-self-review.md`). Windows VHS hangs.
- **Remotion explainers:** Node + `npm install` in a copy of the template.
- If a tool is missing, tell the user exactly what to install before running.

## Brand profiles
- `BRAND_PROFILE=<name>` (default `trustabl`); `example-northwind.json` proves genericity.
- A profile carries the look (`palette`, `logo`, fonts, `grade`), the voice (`voice`,
  `rate`, `pronounce` respellings), the terminal style (`terminal`: canvas size, font
  size, theme, margin colour), and `intro_clip`, the brand's official intro if it has one.
- `python scripts/brand_config.py show <profile>` prints all of it. Schema:
  `references/11-brand-profiles.md`.

## Golden rules (non-negotiable)
1. **Official intro first.** If `python scripts/brand_config.py intro` prints a clip, that
   clip IS the intro: `assemble.py` prepends it. Never generate one for that brand
   (`brand_intro.py` refuses). Trustabl demos: official intro, no outro. The opening
   narration still has to say what the video is for.
2. **Real footage.** A demo shows real commands producing real output, recorded with VHS.
   Never a Pillow slideshow of fake terminal frames unless the user asks for one.
3. **Native pixels.** Record terminals at the canvas size (gentape.py does, from the
   profile). The builders pad, never upscale or stretch, footage that fits the canvas.
4. **English-locked voice** at the brand rate (Trustabl: `en-US-AvaNeural`, `-7%`). The
   builders read both from the profile and refuse `*MultilingualNeural` voices, which
   code-switch on coined words. Respelling cannot fix that; the model is the cause.
5. **You cannot hear audio.** `review.sh` checks sync, spillover, loudness and on-screen
   text; its `pron_suspect` notes mean a human spot-listens that beat.
6. **Verify frames yourself** (`ffmpeg -ss N -i v.mp4 -frames:v 1 f.png`). Vision
   subagents hallucinate on runs of near-identical terminal frames.
7. **Narration:** no structural labels ("Act one", "Part 2", "Step 3"); introduce each beat
   before it lands (the intent line plays while the command types); no em dashes in any
   on-screen text; keep claims to what the footage actually shows.
8. **VHS only in WSL**, as `demo`, with absolute `/home/demo/demo/` paths, and a tape's
   `Output` must be relative. Live timing changes on every take: re-pin after re-recording.

## Terminal demo (the main path)
```bash
python scripts/gentape.py batch.json                 # tapes in the brand's house style
wsl.exe -u demo bash -s <<'EOF'                      # quoted heredoc: wsl.exe mangles $
cd /home/demo/demo && vhs f01.tape
EOF
python scripts/beats.py f01.mp4 --spec spec.json --sheet pins.png   # pins ts/res/end per beat
# look at pins.png, write narration a/b + expect tokens into spec.json
python scripts/vid.py spec.json                      # -> out/<name>.mp4 + <name>.beats.json
bash scripts/review.sh out/<name>.mp4                # in WSL; gate on exit code 0
python scripts/assemble.py out/<name>.mp4 out/joined.mp4          # + official intro
bash scripts/finish.sh out/joined.mp4 final.mp4 demo
```
- `batch.json` (`templates/batch.example.json`): commands may contain double quotes. Env
  the commands need goes in the entry's `setup`: the VHS shell does not reliably source
  `~/.bashrc`, and a missing licence var fails silently behind `2>/dev/null`.
- `beats.py` needs the clear-before-each-command structure gentape emits. For tmux
  dual screens or long streams, pin by hand from a contact sheet. For scroll or stream
  beats that should keep moving under the narration, set `"play_b": true` and use the
  beat's `first_out` as `res`.
- Full detail: `references/02-terminal-demo-factory.md`.

## Explainer video (Remotion)
Copy `templates/remotion-diagrams/`, `npm install`, author `src/specs.tsx` + one narration
mp3 per section (`audioDur` = the mp3's exact ffprobe duration). QA with
`npx remotion still` first, then render `ExplainerWorking` (IntroA + sections, no outro).
4K: `--scale=1.5 --crf=10 --concurrency=2`, in the background (about 30 min per 4 min).
Detail: `references/13-remotion-diagrams.md` and the template README.

## Real Claude Code session
VHS drives `claude` in WSL; `session_vid.py` re-paces the long take from a scenes spec
(`templates/session.example.json`). Detail: `references/03-recording-claude-sessions.md`.

## Brand intro / banner (brands without an official intro)
```bash
BRAND_PROFILE=<p> OUT_DIR=<dir> python scripts/brand_intro.py intro       # or: banner
WORKDIR=<dir> python scripts/sound_gen.py                                 # intro_audio.wav
ffmpeg -i <dir>/intro_silent.mp4 -i <dir>/intro_audio.wav -c:v copy -c:a aac -shortest intro.mp4
GRADE="$(python scripts/brand_config.py grade <p>)" bash scripts/finish.sh intro.mp4 intro_final.mp4 brand
```
`python scripts/brand_intro.py intro mock` renders a 6-frame storyboard first. Detail:
`references/04-brand-intro-and-banner.md`, `references/05-sound-design.md`.

## Finishing (`finish.sh`, always last)
- `demo` mode for anything recorded (terminal, screen capture): deband only, crystal
  clear. The user rejected grain and vignette on narrated terminal footage.
- `brand` mode for motion graphics: deband + the profile's grade + light grain + a soft
  vignette. Explainers use `GRAIN=2`.
- Over ~2 minutes or at 4K pass `FAST=1`. Unknown modes are rejected.

## Long jobs
4K renders and finish passes run far past the Bash tool's 10-minute cap. Start them in
the background from the outset. If a shell does time out, ffmpeg keeps running: check
`tasklist` for it and wait, do not start a second pass on the same output.

## Verification discipline
Run `scripts/review.sh <body.mp4>` on the vid.py/session_vid.py output **before**
assembling and finishing, and gate on its exit code (0 PASS, 1 FAIL, 2 ERROR). It checks
narration-to-visual sync, spillover/double-voice, dead air, loudness/clipping, and
on-screen text (OCR) against the `.beats.json` sidecar. `expect` tokens per beat make the
OCR check precise. After assembling, check the seams and the true last frame yourself.
Detail: `references/12-self-review.md`.

## References
`references/`: 01 pipeline · 02 terminal-demo-factory · 03 recording-claude-sessions ·
04 brand-intro-and-banner · 05 sound-design · 06 voice-models · 07 environment-and-gotchas ·
08 research-report · 09 improvement-plan (historical) · 10 style-guide · 11 brand-profiles ·
12 self-review · 13 remotion-diagrams · brand.md.

## Default template
`templates/remotion-diagrams/` is the default starting point for any brand/product
explainer: the Trustabl Artifacts Explainer system (IntroA bookend, navy `src/brand.ts`
tokens, Instrument Serif + Geist, one accent-tint focal node per figure, `slide()`
between sections; `fade()` superimposes same-position headers, so bookend edges only).
Improve this template rather than forking it ad hoc; add new templates beside it
(`templates/<name>/`) for new video shapes and products.

Template versions are code-named and git-tagged (`template/<codename>-vN`); the
directory at HEAD is always the default:
- **Slipstream (v2, default)**, tag `template/slipstream-v2`: the stateful network
  language (`src/network.tsx`), two-tone headers, the `Spof` example.
- **Harbor (v1)**, tag `template/harbor-v1`: the reveal-only Section/spec model.
  `git checkout template/harbor-v1 -- skills/video-toolkit/templates/remotion-diagrams`.
Remotion is free only for individuals and companies of up to 3 employees; the VHS and
Pillow paths stay the $0 route.
