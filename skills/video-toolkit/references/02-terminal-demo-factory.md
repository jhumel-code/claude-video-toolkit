# 02 · Terminal Demo Factory

For **deterministic CLI demos** (a tool's output is byte-stable). The factory turns
a batch of commands into clean footage, then narrates it with two-phase pacing.

## Flow

```
batch.json ──gentape.py──► one .tape per video
   .tape ──VHS (WSL, demo user)──► footage.mp4   (silent terminal recording)
   footage + spec.json ──vid.py──► finished narrated video (upscaled + zoomed)
```

## Step 1 — `gentape.py <batch.json>`

Emits one clean `.tape` per entry. Standard structure = `clear` before every
command after the first, `Sleep 2s` between typing and Enter (the pause the user
liked), generous hold, `Wait@90s /^> ?$/` to block on the prompt.

`batch.json` shape (see `templates/batch.example.json`):
```json
[
  { "tape": "f01.tape", "out": "f01-myfeature",
    "beats": [ ["trustabl scan .", 4], ["trustabl scan . --vuln-scan", 6] ] }
]
```
- `beats` = `[command, hold_seconds]` pairs.
- **Commands use single quotes only** (the tape's `Type "..."` already uses doubles).

## Step 2 — render in WSL

```bash
# copy tapes into WSL, then:
wsl.exe -u demo bash -s <<'EOF'
cd /home/demo/demo && vhs f01.tape
EOF
```
- **Always absolute `/home/demo/demo/` paths, never `~`** (wsl's default user's home
  differs → files land in the wrong place).
- `Output` in the tape must be **relative** (`Output f01.mp4`), run from the cwd.
- Copy footage back to the Windows working dir.

## Step 3 — pin the beats with `beats.py <footage>`

Runs `freezedetect=n=-50dB:d=0.8`, prints content-change timestamps. Reliable for
the FIRST result of each beat and for clears; **misses the last beat's result** (no
motion after) and over-fires on multi-line streaming output. So: take what it gives,
then frame-read one frame per beat to pin the rest. For a clean clear-before-each
tape the events are `[res1, clear2, res2, clear3, …]`; beatK `ts=event[2K-3]`,
`res=event[2K-2]`.

## Step 4 — `vid.py <spec.json>` (the factory)

Spec (see `templates/spec.example.json`):
```json
{ "name":"07-network-policy", "footage":"f07.mp4", "voice":"en-US-AvaNeural",
  "outdir":"C:/.../out/",
  "beats":[ {"ts":1.5,"res":4.24,"a":"intent line, spoken over the typing",
                                  "b":"explanation, spoken over the result"} ] }
```
- `ts` = typing-start time in the footage, `res` = result-appearance time.
- `a` = the **intent** line (plays while the command types); `b` = the **result**
  line (plays once the result is on screen).
- vid.py synthesizes a/b, does the **two-phase re-pace** (phase A = typing footage
  from `ts`, freeze the pre-result frame to fill the intent line; phase B = result
  footage from `res`, freeze to fill the explanation line), mixes, quality-upscales,
  left-anchored zoom, writes `<outdir><name>.mp4`.

**Two-phase pacing** is the whole trick: the command types while the narrator says
*what it will do*, then the result appears exactly as the narrator starts explaining
it. Fixes "too fast / result-before-setup". One spec + one footage = one video.

## Verify

- Read 1-2 frames per batch (command visible in phase A, result in phase B).
- Check narration: clip durations + `silencedetect` gaps. **Never trust "it sounds
  right"** — you can't hear; the human confirms tone.
