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
- **ffmpeg reads stdin unless told not to.** Inside a `wsl.exe bash -s <<'EOF'` heredoc
  every command shares the heredoc as stdin, so an ffmpeg without `-nostdin` swallows
  the rest of the script (and treats it as keystrokes: a `+` raises its log level). The
  commands after it silently never run. The toolkit's scripts all pass `-nostdin`; do
  the same in ad-hoc ffmpeg lines.
- **Always absolute `/home/demo/demo/` paths, never `~`** — the default wsl user's
  home differs, so `~` silently lands files in the wrong place.
- **VHS `Output` must be a relative path** — an absolute path errors the parser.
- **VHS overrides the prompt to `> `**: `Wait` patterns must match `^> ?$`, not `$`.
- **The VHS/ttyd shell does not reliably source `~/.bashrc`.** Export what the commands
  need (licence keys, PATH) in the hidden setup line (gentape's `setup`). A missing
  licence var behind `2>/dev/null` makes every later beat short-circuit while the
  footage still looks plausible, until someone reads the frames.
- **`Type` strings take `"double"` or `` `backtick` `` delimiters.** Use backticks for a
  command that contains double quotes (gentape does this automatically); only a command
  with both needs a helper script.
- VHS compresses time (frames drop, typing looks faster) and renders at about 3x the
  footage length at 2560x1440. **Never trust tape arithmetic**; pin beats from the
  footage (`scripts/beats.py`) and re-pin after every re-record (warm caches alone moved
  one tape from 93 s to 53 s).
- The cursor blinks by default (about 32 px of "ink" at 640x360); beats.py flattens it.

### ffmpeg
- **`-t` BEFORE `-i`** when freezing with `tpad`: `-t` after `-i` truncates the
  freeze (clip ends short by exactly the freeze length).
- **Input seeking is frame-accurate when re-encoding**, even on VHS footage whose
  keyframes are 10 s apart (verified 2026-09-29 by seeking a counter clip to 7.3 s and
  13.1 s). No all-intra re-encode is needed before cutting; a blank frame after a cut
  means the pin is wrong, not the seek. Only `-c copy` cuts snap to keyframes.
- **Upscaling terminal footage softens text.** The old fixed `scale=2600:1680` chain also
  stretched any footage that was not 1300x840 (2400x1200 came out 29% taller). Record at
  the canvas size; the builders then leave the pixels alone.
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

### Long jobs
- The Bash tool stops a foreground command at 10 minutes. A 4K60 finish pass took 51
  minutes for 223 s of video even with `FAST=1`, and a 4K Remotion render about 30
  minutes for 4 minutes. Start these in the background from the outset.
- A killed shell does NOT kill its ffmpeg child: it keeps writing the output. Check
  `tasklist | grep ffmpeg` and wait for it; a second pass on the same file fails with
  "Device or resource busy".

### Remotion (Windows)
- Render with `--concurrency=2`; higher values crash ffmpeg at DLL init.
- The headless browser is spawned from `node_modules/.remotion/...`; if the project sits
  deep enough that this path passes 260 characters, the launch fails with ENOENT. Move
  the project to a shorter path or pass `--browser-executable=<short path to it>`.
- `audioDur` in `specs.tsx` must equal the narration mp3's duration exactly; it sets the
  section length.

## Where things live (on the build machine)

- Working dir: any folder you choose (`WORKDIR`); builders write clips to `_v_<name>/`
  and cache narration in `_tts/` there.
- Finished videos: the spec's `outdir`; brand intros: `OUT_DIR`.
- WSL render assets: `/home/demo/demo/`.
- Brand assets: this skill's `assets/` (logos, the official Trustabl intro clip).
