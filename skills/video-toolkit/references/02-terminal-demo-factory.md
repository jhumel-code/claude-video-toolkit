# 02 · Terminal Demo Factory

For narrated demos of a CLI: real commands, real output, recorded with VHS, narrated with
two-phase pacing, joined to the brand's official intro.

## Flow

```
batch.json ──gentape.py──► .tape (house style from the brand profile)
   .tape ──VHS (WSL, demo user)──► footage.mp4   (native canvas size, silent)
   footage ──beats.py──► ts / res / end per beat (+ spec skeleton, contact sheet)
   footage + spec.json ──vid.py──► body.mp4 + body.beats.json
   body ──review.sh──► PASS / FAIL (gate)
   intro + body ──assemble.py──► joined.mp4 ──finish.sh demo──► final.mp4
```

## Step 1: `gentape.py <batch.json>`

One `.tape` per entry, in the brand profile's `terminal` style (2560x1440, FontSize 28,
the brand theme and margin colour for Trustabl), recorded at the video canvas size so the
builder never scales it. Structure: a hidden setup line, then per beat: type, pause, Enter,
`Wait@90s /^> ?$/`, hold; `clear` before every command after the first.

```json
[ { "tape": "f01.tape", "out": "f01-myfeature",
    "cwd": "/home/demo/demo", "setup": "source ./demo-env.sh",
    "beats": [ ["trustabl scan .", 4], ["jq -r \".findings | length\" scan.json", 6] ] } ]
```
- `beats` = `[command, hold_seconds]`. Hold at least 2 s, so the 1.5 s of result footage
  that vid.py plays stays inside the hold. Scroll/stream beats that play under their
  narration need a hold as long as that line.
- `setup` runs hidden before recording. Put every env var the commands need here: the
  VHS/ttyd shell does not reliably source `~/.bashrc`, and a missing licence var fails
  silently when stderr goes to `/dev/null`, leaving plausible-looking but wrong footage.
- Commands may contain double quotes: gentape types them with backtick delimiters.
  A command with both `"` and a backtick must move into a helper script.
- Optional per entry: `pause` (seconds between typing and Enter, default 2), `wait`.

## Step 2: record in WSL

```bash
cat f01.tape | wsl.exe -u demo bash -c 'cat > /home/demo/demo/f01.tape'
wsl.exe -u demo bash -s <<'EOF'
cd /home/demo/demo && vhs f01.tape
EOF
```
- Absolute `/home/demo/demo/` paths, never `~`; `Output` in the tape stays relative.
- VHS renders slowly at 2560x1440 (about 3x the footage length) and compresses time:
  pin beats in footage time, never from tape arithmetic.

## Step 3: pin the beats with `beats.py`

```bash
python scripts/beats.py f01.mp4 --spec spec.json --sheet pins.png
```
It measures the footage's ink (bright text pixels) at 12.5 fps and reads the tape's
shape: a clear drops ink to the floor, typing raises it slowly, the pause holds it flat,
output raises it in jumps. The cursor blink is flattened first. Per beat:
- `ts` typing starts, `first_out` output starts, `res` output about complete (97% of the
  beat's plateau, so streaming output is waited out), `end` the last frame before the
  next `clear` is typed.
- `--spec` writes a vid.py skeleton with ts/res/end; `--sheet` tiles the exact frame
  vid.py will hold in phase B for every beat. **Look at the sheet before building.**
- A `short hold` warning means the result is on screen under 1.5 s before its clear.
- Only for clear-before-each tapes. tmux dual screens and long single streams: pin by
  hand from a contact sheet (`ffmpeg -i f.mp4 -vf "fps=1/2,scale=520:-1,tile=6x6"`).

## Step 4: `vid.py <spec.json>`

```json
{ "name": "07-network-policy", "footage": "f07.mp4", "outdir": "out",
  "beats": [ { "ts": 1.5, "res": 4.24, "end": 17.4,
               "a": "intent line, spoken over the typing",
               "b": "explanation, spoken over the result",
               "expect": ["token on screen at the result"] } ] }
```
- **Two-phase pacing**: phase A plays the typing from `ts` under `a` and holds the last
  pre-result frame if the line is longer; phase B plays 1.5 s from `res` under `b`, then
  holds. The narrator introduces the command before its result lands.
- `"play_b": true` keeps phase B playing (scrolls, streaming output) for `play_dur`
  seconds (default: the line's length), then holds. Use the beat's `first_out` as `res`.
- `end` stops any playback at the beat's own last frame, so a short hold can never freeze
  on the next command being typed. Keep the value beats.py wrote.
- Optional per beat: `footage` (a second recording), `expect_a`, `scroll_top`.
- Top level: `brand`, `tts` (the voice engine, e.g. `{"engine": "kokoro", "voice":
  "af_heart", "speed": 0.93}`; see `14-narration-voice.md`), `voice`/`rate` (edge-tts
  shorthand), `canvas`, `fit` (`pad` default, `scale` to upscale small legacy footage),
  `pad_color`, `gap`. The voice defaults to the brand profile; multilingual voices are
  refused. Every line is linted before it's voiced (warnings print, errors stop).
- Output: `<outdir>/<name>.mp4` at the canvas size, plus `<name>.beats.json` for
  review.sh. Each clip is encoded once; narration sits at the measured clip boundaries.
  TTS clips are cached in `WORKDIR/_tts/`, so re-running after a pin change is fast.

## Step 5: review, assemble, finish

```bash
bash scripts/review.sh out/07-network-policy.mp4          # in WSL; exit 0 = PASS
python scripts/assemble.py out/07-network-policy.mp4 out/joined.mp4   # official intro, no outro
bash scripts/finish.sh out/joined.mp4 final.mp4 demo
```
Then check the seams and the true last frame yourself (`-sseof -0.1`).

## Narration

- The `a` line says what the command will do; the `b` line explains what is on screen.
  Never claim something the footage does not show.
- Result-claim lines lead with a soft connective ("And it's blocked"): a bare
  hard-consonant opener gets a cold emphatic tone from edge-tts.
- Spell initialisms and numbers the way they should be said ("A-I agent", "zero point
  seven one"); coined words go through the pronounce map.
- No structural labels ("Act one", "Step 3"); the sentences carry the transitions.
