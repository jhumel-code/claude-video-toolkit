#!/usr/bin/env python3
"""vid.py <spec.json> -> <outdir>/<name>.mp4 + <name>.beats.json (the review.sh sidecar)

Two-phase narrated terminal demo. For each beat:
  phase A  footage from `ts` (the command typing) under the intent line `a`; if the line
           outlasts the typing, the last frame before the result is held;
  phase B  footage from `res` (the result appearing) under the explanation `b`. It plays
           1.5 s and then holds the result frame, or with "play_b": true it keeps playing
           (scrolls, streaming output) for play_dur (default: the narration), then holds.
           With the beat's `end` (from beats.py), playback never runs past it into the
           next command; the beat's last frame is held instead.

Spec (templates/spec.example.json): name, footage, beats[] of {ts, res, a, b} plus optional
  top level: outdir, brand, tts ({"engine": "kokoro", "voice": "af_heart", "speed": 0.93},
             see references/14-narration-voice.md), voice/rate (edge shorthand), canvas
             ("2560x1440"), fit ("pad"|"scale"), pad_color, gap (silence after each line, 0.4)
  per beat:  end, footage (a second recording), expect_a / expect (OCR tokens for
             review.sh), scroll_top, play_b, play_dur
Voice and rate default to the brand profile (BRAND_PROFILE). Paths resolve from WORKDIR.
Pin ts/res with scripts/beats.py.
"""
import json, sys
from narrate import Build, dur

HOLD_B = 1.5   # seconds of result footage before phase B holds the frame

spec = json.load(open(sys.argv[1], encoding="utf-8"))
B = Build(spec)
B.lint([(f"b{i}{k}", b[k]) for i, b in enumerate(spec["beats"]) for k in ("a", "b")])
for i, b in enumerate(spec["beats"]):
    src = B.footage(b.get("footage"))
    ts, res = float(b["ts"]), float(b["res"])

    mp3 = B.tts(b["a"])
    need = dur(mp3) + B.gap
    play = max(0.4, min(need, res - 0.1 - ts))
    B.add(f"b{i}a", "intent", b["a"], mp3, B.clip(src, ts, play, need, f"{i}a"),
          expected=b.get("expect_a"))

    mp3 = B.tts(b["b"])
    need = dur(mp3) + B.gap
    if b.get("play_b"):
        play = float(b.get("play_dur") or need)
        need = max(need, play)
    else:
        play = min(need, HOLD_B)
    if b.get("end") is not None:   # never play into the next command; hold this beat's last frame
        play = min(play, float(b["end"]) - res)
    B.add(f"b{i}b", "result", b["b"], mp3, B.clip(src, res, play, need, f"{i}b"),
          expected=b.get("expect"), scroll_top=b.get("scroll_top"), play_b=b.get("play_b"))
B.finish()
