# Claude Video Toolkit (plugin)

Produce **brand intros**, **animated banners**, and **narrated terminal/CLI demo
videos** — and record real Claude Code sessions — fully from the command line.
Deterministic, free (Pillow/numpy + ffmpeg + VHS + edge-tts; no paid tools), and
**brand-agnostic**: brand identity is a JSON profile, so the same engine produces
on-brand video for any product. Trustabl ships as the worked example profile.

## Components
- **Skill: `video-toolkit`** — the full workflow + bundled scripts, brand profiles,
  fonts, assets, templates, and reference docs.

(No agents or MCP servers — the pipeline runs through Bash + the bundled scripts.)

## Setup / prerequisites
- **WSL Ubuntu** with `vhs` + `ttyd` + chromium libs (terminal recording only;
  brand intros/banners + finishing don't need it). Record as a non-root `demo` user.
- **Host:** `ffmpeg` + `ffprobe`; Python 3 with `pip install edge-tts pillow numpy`;
  optional `sox` for richer sound. The skill front-loads these checks.

## Usage
Trigger by asking for a video: "make a brand intro", "create an animated banner",
"record a terminal demo", "make a demo video", "finish/grade this video". Choose a
brand with `BRAND_PROFILE=<name>` (default `trustabl`); add your own brand by copying
`profiles/example-northwind.json`. See the skill's `references/11-brand-profiles.md`.
