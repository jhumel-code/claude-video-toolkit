# 06 · Voice Models & Narration

Narration is **edge-tts** (Microsoft Edge neural TTS): free, no API key.

```bash
python -m edge_tts --voice en-US-AvaNeural --rate=-7% --text "..." --write-media out.mp3
python -m edge_tts --list-voices | grep en-US        # list voices
```

The builders (`vid.py`, `session_vid.py`) take the voice and rate from the spec, else the
brand profile (`voice`, `rate`), and pass the rate as ONE token (`--rate=-7%`): as two
tokens argparse reads `-7%` as a flag and edge-tts exits 2. Trustabl's rate is `-7%`
(the user found the natural rate too fast; `-10%` sounded robotic). A narration clip is
reproducible to the millisecond: one edge-tts call per clip, same voice, rate and
respelled text, no hand-inserted silences.

> **Hear them:** [`../voices/`](../voices/) has a comparable sample of every voice
> we use (same sentence) plus a table of where/how each one is used. Play
> `AvaNeural` vs `AvaMultilingualNeural` to hear the code-switch issue described below.

## The one rule that matters

**Narrate with `en-US-AvaNeural` — the English-locked voice. NEVER the
`*MultilingualNeural` variants.**

The `*MultilingualNeural` voices (AvaMultilingual / AndrewMultilingual /
EmmaMultilingual) auto-detect language per segment and **code-switch into another
language's phonology on coined / non-dictionary words**. The brand name "Trustabl"
triggered a foreign-sounding blip mid-sentence across an entire 54-video batch.

- `en-US-AvaNeural` is the **same Ava timbre**, locked to English, ~0.8% shorter —
  it physically cannot switch language. Use it.
- edge-tts is **byte-deterministic** (same text + voice → identical mp3), so the
  glitch is reproducible and a **spelling change won't fix it** (`Trustabl` and
  `Trustable` render byte-identical in the mono voice). The *model* is the cause.

## Narration text hygiene (so TTS reads cleanly)

- Spell initialisms: write **"A-I agent"**, **"C-I"** (so it says "A I", not "ai").
- Spell numbers as words for scores: **"zero point seven one"**, **"one point zero"**.
- Don't put rule IDs / code tokens in narration — they read awkwardly.
- Result-claim lines ("And it's blocked", "And it works") are **separate clips
  placed AFTER the on-screen result**, and should **lead with a soft connective** —
  a bare hard-consonant opener ("Blocked.") makes edge-tts use a cold emphatic tone
  that won't blend.

## Voice pacing (if you ever change voice)

Ava ≈ Andrew ≈ Emma in pace; **Aria/Jenny ~15% slower**. The multi-voice swap
trick (below) only works when the new voice paces within ~1-2% of the reference.

## Re-voice / fix audio on a FINISHED video

Swap the narration of an already-rendered video without re-recording or re-encoding
the picture: re-synthesize each line with the new voice, place it at the
`narr_start_s` recorded in the video's `.beats.json` sidecar (atempo-fit only a clip
that would overrun its slot), and mux onto the copied video stream
(`-map 0:v -c:v copy`). Flag any clip that needed more than a 5% speed-up for an
ear-check. Simpler still: change `voice`/`rate` in the spec and re-run vid.py, which
reuses the footage.

`scripts/legacy/reaudio.py` is the one-off version of this that moved a 54-video batch
off the multilingual voice after the footage was deleted (it recovered the slot times
by re-synthesizing the old voice, which is byte-deterministic). The June multi-voice
swap scripts (`make_voice.sh`, `build_voice.sh`, `fit_body.py`) are there too: they
only work when the new voice paces within ~1-2% of the reference.

## Hard limit

**You (the model) cannot hear audio.** Verify narration objectively — clip
durations, `silencedetect` gap structure, frame timestamps — and have the **human
confirm** tone / pronunciation / "does it sound right". For pronunciation A/Bs,
generate a labelled comparison (numbered spoken labels between the options, stitched
into one `COMPARE_listen_to_this.mp3`; `scripts/legacy/build_compare.py` is the
worked example) and let them pick.
