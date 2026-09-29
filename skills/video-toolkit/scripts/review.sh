#!/bin/bash
# review.sh <video.mp4> [beats.json]
# Self-review a rendered narrated video WITHOUT a human watching: audio quality + narration
# sync/spillover + visual OCR, all keyed off the <video>.beats.json sidecar the builder emits.
# Prints (and writes to <video>.review/review.txt) one verdict line, then one line per failing
# beat and one per note (pron_suspect notes mean: spot-listen that beat). Gate on the EXIT CODE:
# 0 PASS, 1 FAIL, 2 ERROR (no sidecar, missing tool, or transcription failed).
# Drill-down artifacts in <video>.review/: words.json, qa_audio.json, qa_visual.json, sig.log.
set -uo pipefail
VID="${1:?usage: review.sh <video.mp4> [beats.json]}"
BEATS="${2:-${VID%.*}.beats.json}"
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="$(cd "$(dirname "$VID")" && pwd)"
VIDABS="$WORK/$(basename "$VID")"
[ -f "$BEATS" ] || BEATS="$WORK/$(basename "$BEATS")"
[ -f "$BEATS" ] && BEATS="$(cd "$(dirname "$BEATS")" && pwd)/$(basename "$BEATS")"
RDIR="$WORK/$(basename "${VID%.*}").review"
mkdir -p "$RDIR" && cd "$RDIR" || exit 2
# never let a stale artifact from an earlier review stand in for this one
rm -f review.txt words.json qa_audio.json qa_visual.json sig.log audio.wav

verdict() { { echo "$1"; printf '%b\n' "$2" | sed '/^[[:space:]]*$/d'; } | tee review.txt; }

if [ ! -f "$BEATS" ]; then
  verdict "VERDICT: ERROR  no beats.json sidecar ('$BEATS') - rebuild with a sidecar-emitting builder (vid.py emits <name>.beats.json)" ""
  exit 2
fi
source "$HERE/stt-env.sh" 2>/dev/null || true
# a missing tool must not masquerade as a video defect (no OCR = every beat "sparse")
MISSING=""
command -v tesseract >/dev/null 2>&1 || MISSING="$MISSING tesseract-ocr"
python3 -c "import faster_whisper" 2>/dev/null || MISSING="$MISSING faster-whisper"
if [ -n "$MISSING" ]; then
  verdict "VERDICT: ERROR  missing:$MISSING - one-time setup in references/12-self-review.md" ""
  exit 2
fi
NB=$(python3 -c "import json;d=json.load(open(r'$BEATS'));print(len(d['beats'] if isinstance(d,dict) else d))" 2>/dev/null || echo "?")
FAIL=0; ISSUES=""; NOTES=""
collect() {  # collect <exit code> <output>: failures and notes kept apart
  NOTES="$NOTES"$'\n'"$(printf '%s\n' "$2" | grep 'note:')"
  [ "$1" -ne 0 ] && { FAIL=1; ISSUES="$ISSUES"$'\n'"$(printf '%s\n' "$2" | grep -v 'note:')"; }
}

# 1. structural sanity
HASA=$(ffprobe -v error -select_streams a -show_entries stream=codec_type -of csv=p=0 "$VIDABS" 2>/dev/null)
[ -z "$HASA" ] && { FAIL=1; ISSUES="$ISSUES"$'\n'"  structural: no audio stream"; }

# 2. audio signal: loudness / clipping / grossly-long silence (one ffmpeg pass)
ffmpeg -nostdin -hide_banner -nostats -i "$VIDABS" -af "silencedetect=n=-40dB:d=2.5,ebur128=peak=true,volumedetect" -f null - 2>sig.log || true
OUT=$(python3 "$HERE/qa_signal.py" sig.log); collect $? "$OUT"

# 3. transcribe narration to word-timestamped JSON
ffmpeg -nostdin -y -v error -i "$VIDABS" -vn -ac 1 -ar 16000 audio.wav
if ! python3 "$HERE/transcribe.py" audio.wav words.json || [ ! -s words.json ]; then
  verdict "VERDICT: ERROR  transcription failed - see the transcribe.py error above" ""
  exit 2
fi
rm -f audio.wav

# 4. narration sync / spillover / content / pronunciation (keyed off beats.json)
OUT=$(python3 "$HERE/qa_audio.py" words.json "$BEATS"); collect $? "$OUT"

# 5. visual OCR: blank / wrong / scroll-incomplete
OUT=$(python3 "$HERE/qa_visual.py" "$VIDABS" "$BEATS"); collect $? "$OUT"

NN=$(printf '%s\n' "$NOTES" | grep -c 'note:')
if [ "$FAIL" -eq 0 ]; then
  verdict "VERDICT: PASS ($NB beats, 0 issues, $NN notes)" "$NOTES"
  exit 0
fi
verdict "VERDICT: FAIL" "$ISSUES$NOTES"
exit 1
