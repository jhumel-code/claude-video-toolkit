# Claude Video Toolkit (plugin)

Produce **narrated terminal/CLI demo videos**, **animated diagram explainers**,
recorded Claude Code sessions, **brand intros** and **animated banners**, fully from
the command line. Deterministic and free (VHS + edge-tts + ffmpeg + Pillow/numpy; the
Remotion template is free for individuals and small teams), and **brand-agnostic**:
brand identity (look, voice, terminal theme, official intro) is a JSON profile, so the
same engine produces on-brand video for any product. Trustabl ships as the worked
example profile.

The terminal-demo path in one screen:
```bash
python scripts/gentape.py batch.json                         # tapes in the brand's house style
vhs f01.tape                                                 # (in WSL) record real footage
python scripts/beats.py f01.mp4 --spec spec.json --sheet pins.png   # pin every beat
python scripts/vid.py spec.json                              # narrate: body + review sidecar
bash scripts/review.sh out/f01.mp4                           # (in WSL) self-review gate
python scripts/assemble.py out/f01.mp4 out/joined.mp4        # + the brand's official intro
bash scripts/finish.sh out/joined.mp4 final.mp4 demo
```
(scripts live in `skills/video-toolkit/scripts/`)

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
- **WSL Ubuntu** with `vhs` + `ttyd` + chromium libs (terminal recording), plus
  `tesseract-ocr` and `faster-whisper` for the self-review pass. Record as a non-root
  `demo` user. Brand intros/banners and finishing don't need WSL.
- **Host:** `ffmpeg` + `ffprobe`; Python 3 with `pip install edge-tts pillow numpy`;
  optional `sox` for richer sound; Node for the Remotion template. The skill
  front-loads these checks.

## Usage
Trigger by asking for a video: "make a demo video", "record a terminal demo", "make an
explainer video", "make a brand intro", "create an animated banner", "finish/grade this
video". Choose a brand with `BRAND_PROFILE=<name>` (default `trustabl`); add your own
brand by copying `profiles/example-northwind.json`. See the skill's
`references/11-brand-profiles.md`.

## Releasing an update
The installed plugin is a versioned copy, so a pushed change only reaches new sessions
when the version moves. For each release:
1. Bump `version` in `.claude-plugin/plugin.json`, the matching entry in
   `.claude-plugin/marketplace.json`, and `metadata.version` in `SKILL.md`, then
   `claude plugin validate .`
2. Commit and push to `main`.
3. `claude plugin marketplace update jhumel-code`, then
   `claude plugin update claude-video-toolkit@jhumel-code`, and restart Claude Code.
Version 0.1.0 never changed, which is why the installed copies were being hand-synced
(and drifted).

## Templates
`skills/video-toolkit/templates/remotion-diagrams/` is the **Remotion animated
diagram-explainer template** — the default starting point for any brand/product
explainer video (React→video: narrated sections, eased reveals, slide transitions,
banding-free backgrounds). It ships with everything the examples need (fonts,
logos, narration audio), so after `npm install` the renders work out of the box —
see `NOTICE.md` for asset licensing, and note Remotion's own license (free only for
individuals and ≤3-employee companies).

Template versions are **code-named and git-tagged**; the directory at HEAD is
always the current default:

| Codename | Tag | What it is |
|---|---|---|
| **Slipstream** (v2, default) | `template/slipstream-v2` | Adds the stateful network language: curved flow edges with travelling particles, nodes that flip live→down on a narration-synced timeline, stat cards, caption beats, two-tone headers, and the `Spof` slide-deck example. |
| **Harbor** (v1) | `template/harbor-v1` | The original reveal-only diagram explainer: data-spec sections (nodes/arrows/code cards), navy skin, Instrument Serif + Geist. |

To use an older version without rolling back the repo:
```bash
git checkout template/harbor-v1 -- skills/video-toolkit/templates/remotion-diagrams
```
