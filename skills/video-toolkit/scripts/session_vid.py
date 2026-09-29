#!/usr/bin/env python3
"""session_vid.py <spec.json> -> <outdir>/<name>.mp4 + <name>.beats.json

Narrated re-pace of ONE long take (e.g. a real Claude Code session recorded with VHS).
Each scene is narrated once and sources its picture one of two ways:
  "mode": "speed"   footage [in, out] time-stretched to the narration length (action spans)
  "mode": "freeze"  a single frame at `at` held for the narration (tables, final scores)

Spec (templates/session.example.json): name, footage, scenes[] of {t, mode, in/out | at}
plus optional outdir, brand, voice, rate, canvas, fit, pad_color, gap, and per scene
`footage` and `expect` (OCR tokens for review.sh). Paths resolve from WORKDIR.
Pull narration-accurate content from the session transcript, not from squinting at frames.
"""
import json, sys
from narrate import Build, dur

spec = json.load(open(sys.argv[1], encoding="utf-8"))
B = Build(spec)
for i, s in enumerate(spec["scenes"]):
    src = B.footage(s.get("footage"))
    mp3 = B.tts(s["t"])
    need = dur(mp3) + B.gap
    if s["mode"] == "freeze":
        clip = B.clip(src, float(s["at"]), 0, need, f"s{i}")
    elif s["mode"] == "speed":
        clip = B.stretch(src, float(s["in"]), float(s["out"]), need, f"s{i}")
    else:
        sys.exit(f"scene {i}: mode must be 'speed' or 'freeze', got {s['mode']!r}")
    B.add(f"s{i}", "result", s["t"], mp3, clip, expected=s.get("expect"))
B.finish()
