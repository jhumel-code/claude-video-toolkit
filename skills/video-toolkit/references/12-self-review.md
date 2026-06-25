# 12 - Self-review (catch issues before a human does)

Frame-grabbing alone cannot verify a narrated video: it shows what is *on screen* but not
whether the *narration* lines up with it, nor how it sounds. `scripts/review.sh` closes that
gap. It runs cheap local passes against a render and emits a pass/fail report keyed off the
`beats.json` sidecar the builders emit, so the agent gates regeneration on the report instead
of shipping bugs a human then has to find.

## Run it

```bash
WORKDIR=/path/to/work bash scripts/review.sh out.mp4            # beats.json auto: out.beats.json
bash scripts/review.sh out.mp4 out.beats.json                  # explicit sidecar
echo $?    # 0 PASS, 1 FAIL, 2 ERROR (no sidecar)
cat review.txt
```

Review the **body** render (the builder output, which has the matching sidecar), before you
grade + concat the brand intro/outro. A clean body is the gate to finishing.

## What it checks (and what each catches)

| Pass | Tool | Catches |
|------|------|---------|
| structural | ffprobe | missing audio stream, wildly wrong duration |
| audio signal | ffmpeg `silencedetect`+`ebur128`+`volumedetect` (`qa_signal.py`) | loudness off the -17 LUFS target, clipping, grossly-long silence |
| transcribe | faster-whisper (`transcribe.py`) | (produces `words.json`) |
| sync/spillover | `qa_audio.py` (words.json + beats.json) | **narration drift, spillover/double-voice, wrong narration, suspected mispronunciation, dead air** |
| visual | Tesseract OCR at beat midpoints (`qa_visual.py`) | blank / wrong / scroll-incomplete visuals |

We deliberately do **not** use ffmpeg `freezedetect`/`blackdetect`: this pipeline freezes
frames on purpose (holds, scroll tails), so they would false-positive. Blank visuals are
caught by OCR instead.

## Report format

`review.txt` is two-tier and exit-code-gated so a clean run costs ~0 tokens:
- PASS: one line - `VERDICT: PASS (28 beats, 0 issues)`.
- FAIL: `VERDICT: FAIL` then one line per failing beat, e.g.
  `b12a @256.8s content_mismatch ratio=0.55 | heard:"..."` or
  `b04 @11.0s scroll_incomplete top_missing=docstring`.
Drill-down artifacts stay on disk: `words.json`, `qa_audio.json`, `qa_visual.json`, `sig.log`.

Flag vocabulary (fixed enum): `drift`, `overrun` (spillover), `dead_air`, `blank_visual`,
`wrong_visual`, `scroll_incomplete`, `clipping`, `loudness`, `pron_suspect`, `content_mismatch`,
`no_speech_in_window`.

## The beats.json sidecar contract (load-bearing)

`vid.py` / `vid_slow.py` / `session_vid.py` write `<name>.beats.json` at render time. Without
it, review would have to reverse-engineer ffmpeg timing - the exact failure mode that let
sync bugs slip through. Schema:

```json
{"beats":[
  {"id":"b1b","kind":"result","narr_start_s":42.9,"narr_text":"A readiness score ...",
   "beat_end_s":57.0,"jargon":["SDKs"],"expected_onscreen":["findings","96"],"scroll_top":["docstring"]}
]}
```
- `narr_start_s` / `beat_end_s` are in the **render's own timeline**. If you review a video
  with a brand intro prepended, either review the body before concat, or offset the sidecar.
- `expected_onscreen` (optional): tokens the script knows appear on screen at that beat -
  drives the OCR check. Omit to skip OCR for that beat.
- `scroll_top` (optional): first-lines tokens of a scrolled file - verifies the top was shown
  (catches the "frozen on the bottom" bug).
- `jargon`: terms from `profiles/pronounce.json` present in the narration - drives `pron_suspect`.

## Prevention beats detection - pronounce.json

`profiles/pronounce.json` maps jargon to a spoken form and is applied to narration **before**
edge-tts (which has no phoneme/SSML control - text respelling is the only lever). When review
flags `pron_suspect` on a new term, add one entry and re-synth just that beat's mp3. See
`06-voice-models.md`.

## Honest limit

ASR cannot truly *hear* pronunciation - Whisper may silently auto-correct a mangled word, so
`pron_suspect` is a heuristic (mistranscription + low word probability), not proof. A 5-second
human spot-listen on flagged beats stays the final backstop. Everything else - sync, spillover,
dead air, blank/wrong/scroll-incomplete visuals, loudness, clipping - is caught deterministically.

## One-time WSL setup

```bash
sudo apt-get install -y tesseract-ocr
python3 -m pip install --user faster-whisper nvidia-cublas-cu12 'nvidia-cudnn-cu12==9.*'
```
`scripts/stt-env.sh` (sourced by review.sh) sets `LD_LIBRARY_PATH` to the nvidia wheels'
lib dirs - the #1 WSL gotcha (`Could not load libcudnn_ops.so.9`). If CUDA still fails,
`transcribe.py` auto-falls-back to CPU int8; or `export STT_DEVICE=cpu`.

## Tunable thresholds (env vars)

`QA_SYNC` (1.0s drift), `QA_OVERRUN` (0.7s spillover, > whisper word-timestamp noise),
`QA_RATIO` (0.55 content match), `QA_PWORD` (0.4 word-prob for pron), `QA_DEADAIR` (2.5s),
`QA_LUFS_LO/HI` (-19/-15), `QA_CLIP` (-0.1 dB), `STT_MODEL` (small.en).
