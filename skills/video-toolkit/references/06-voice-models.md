# 06 · Voice Models & Narration

Narration is **edge-tts** (Microsoft Edge neural TTS): free, no API key.

```bash
python -m edge_tts --voice en-US-AvaNeural --text "..." --write-media out.mp3
python -m edge_tts --list-voices | grep en-US        # list voices
```

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

## Re-voice / fix audio on a FINISHED video — `reaudio.py`

Swap the narration of an **already-rendered** video in place, no re-record, no
picture re-encode:

```bash
python vo/reaudio.py <spec.json> <finished_video.mp4> <out.mp4>
# batch over many: vo/reaudio_batch.sh
```

How it works: re-synth each clip with the OLD voice to recover the exact original
slot durations (byte-deterministic), reconstruct the timeline, drop NEW-voice clips
on the identical starts (atempo-fit only if a clip would overrun), then mux onto the
**copied** video stream (`-map 0:v -c:v copy`). Picture stays bit-identical;
alignment preserved; fully reversible (back up originals first). This is how a whole
54-video batch was switched off the multilingual voice after the source footage was
already deleted. Watch the log for `max_atempo > 1.05` (a clip that needed a >5%
speed-up) → flag those for an ear-check.

## The multi-voice swap (older pipeline, optional)

`make_voice.sh <edge-voice> <prefix>` synthesizes a full clip set in a voice;
`build_voice.sh <prefix>` rebuilds a v17-style demo by mixing the new clips at the
**reference voice's beat starts** (no re-pace). `build_intro_voice.py` rebuilds the
intro to each clip's real duration; `fit_body.py` is the safety net that atempo-fits
any clip that would overrun its slot (prevents double-voice). Use only when the new
voice paces ≈ the reference; a much slower voice needs a real re-pace.

## Hard limit

**You (the model) cannot hear audio.** Verify narration objectively — clip
durations, `silencedetect` gap structure, frame timestamps — and have the **human
confirm** tone / pronunciation / "does it sound right". For pronunciation A/Bs,
generate a labelled comparison (`build_compare.py` stitches numbered options into
one `COMPARE_listen_to_this.mp3`) and let them pick.
