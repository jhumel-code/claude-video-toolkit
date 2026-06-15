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

## Install in Claude Code
This repo is a Claude Code plugin **and** its own plugin marketplace, so you can
install it straight from the repo. Run these inside a Claude Code session:

1. Add the marketplace (points Claude Code at this repo):
   ```
   /plugin marketplace add jhumel-code/claude-video-toolkit
   ```
2. Install the plugin:
   ```
   /plugin install claude-video-toolkit@jhumel-code
   ```
   Here `claude-video-toolkit` is the **plugin** and `jhumel-code` is the
   **marketplace** name (they're separate identifiers).
3. If it doesn't activate right away, reload:
   ```
   /reload-plugins
   ```

Prefer a menu? Run `/plugin`, open **Marketplaces** and add
`jhumel-code/claude-video-toolkit`, then open **Discover** and install
**claude-video-toolkit**. Manage or remove it later with `/plugin` (or
`/plugin uninstall claude-video-toolkit@jhumel-code`).

> Installing the plugin gives Claude Code the `video-toolkit` skill. You still
> need the runtime tools below for renders to actually run.

### Team / non-interactive setup
Commit this to the project's `.claude/settings.json` to register the marketplace
and enable the plugin automatically (applied on the next session once the repo is
trusted):
```json
{
  "extraKnownMarketplaces": {
    "jhumel-code": {
      "source": { "source": "github", "repo": "jhumel-code/claude-video-toolkit" }
    }
  },
  "enabledPlugins": {
    "claude-video-toolkit@jhumel-code": true
  }
}
```

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
