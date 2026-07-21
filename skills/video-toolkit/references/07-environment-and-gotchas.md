# 07 · Environment & Gotchas

## WSL setup (one-time, the `demo` user)

VHS renders via headless Chromium which **refuses to run as root** → everything
runs as a non-root user (`demo`). Installed in WSL Ubuntu:
- `vhs` (charmbracelet) + `ttyd` in `/usr/local/bin`
- `ffmpeg` + chromium shared libs (apt)
- assets under `/home/demo/demo/` (binaries, demo repos, tapes)
- (for Claude-session recording) Node 20 + `@anthropic-ai/claude-code` — see
  [03-recording-claude-sessions](03-recording-claude-sessions.md).

Render command shape:
```bash
wsl.exe -u demo bash -s <<'EOF'
cd /home/demo/demo && vhs mytape.tape
EOF
```

## Gotchas (each one cost real time)

### WSL / VHS
- **Windows VHS hangs** (never spawns ttyd). WSL only. Don't retry Windows.
- **`wsl.exe` mangles `$` in arguments** (re-parses argv through a shell). Pass
  scripts via a **quoted stdin heredoc** (`wsl bash -s <<'EOF' … EOF`), never inline
  `$` in `wsl bash -c '...'`. (A big Windows `$PATH` with spaces/parens also breaks
  inline commands → use the heredoc.)
- **Always absolute `/home/demo/demo/` paths, never `~`** — the default wsl user's
  home differs, so `~` silently lands files in the wrong place.
- **VHS `Output` must be a relative path** — an absolute path errors the parser.
- **VHS overrides the prompt to `> `** — `Wait` patterns must match `^> ?$`, not `$`.
- VHS renders ~12% faster than the typing+sleep arithmetic suggests — **never trust
  the math**, pin beats from frames (`freezedetect` / contact sheets).

### ffmpeg
- **`-t` BEFORE `-i`** when freezing with `tpad` — `-t` after `-i` truncates the
  freeze (clip ends short by exactly the freeze length).
- **`drawtext` segfaults on Windows ffmpeg** (no fontconfig). Use WSL ffmpeg for
  `drawtext`, or render text with Pillow instead.
- **Center-anchored zoom on left-aligned terminal text "slides sideways"** — anchor
  `x=0`. Zoom only sparse/static beats; dense scrolling text clips into the padding.
- **Grade before scale bands flat backgrounds** — `deband`'s dither + a
  `curves`/`eq` contrast lift, applied at a lower resolution and THEN upscaled,
  alias into a faint but visible periodic band pattern on flat backgrounds
  (worst on a rational-ratio resize like 2560→3840, i.e. 3:2). Invisible at
  native res and in a thumbnail; only shows up in a native-resolution 1:1
  pixel crop of a flat area. Each filter is clean in isolation — it's the
  *order* that's wrong. Fix: always `scale` first, grade after. `finish.sh`'s
  `SCALE=` env var does this correctly; don't hand-rebuild the chain with scale
  last. Found 2026-07-21 on the OpenShell demo v9→v10 after the user asked to
  check for "any unusual texture, no matter how small."
- **Multiple separate encode passes compound artifacts** — chaining independent
  ffmpeg runs (grade pass → scale pass → concat pass) each re-quantizes the
  image, most visible as mottling on anti-aliased edges (rounded window
  corners). Collapse the whole chain into one `-filter_complex` graph with a
  single final `-c:v libx264` encode instead.

### Audio
- **You can't hear** — verify by durations + `silencedetect` gaps; human confirms tone.
- **`requirements.txt` (and any file) must end with a trailing newline** or VHS
  `Wait /^> ?$/` hangs (the prompt glues to the last line).
- Multilingual TTS voices code-switch — see [06-voice-models](06-voice-models.md).

### Files / determinism
- **CRLF**: Windows tools may write CRLF; if a file is consumed by a LF-only tool,
  convert. (In the Trustabl repo, `.gitattributes` forces `eol=lf` on `*.go`/`*.md`.)
- **Live VHS render timing is non-deterministic** (sandbox/AI latency varies → every
  beat shifts). Re-pin beats every render; **freeze result frames** so they can't drift.
- **Vision subagents hallucinate** on long runs of near-identical terminal frames —
  verify load-bearing frames yourself by seeking (25 fps CFR mp4s seek reliably).

## Where things live (on the build machine)

- Working dir: any folder you choose (set `WORKDIR`), holding `vo/` (scripts) + `fonts/`.
- Finished videos: your chosen output dir (set `OUT_DIR`).
- WSL render assets: `/home/demo/demo/`.
- Brand assets: the Trustabl engine repo `assets/` (see [brand.md](brand.md)).
