#!/bin/bash
# review.sh <video.mp4> [beats.json]
# Self-review a rendered narrated video WITHOUT a human watching: audio quality + narration
# sync/spillover + visual OCR, all keyed off the <video>.beats.json sidecar the builder emits.
# The agent reads review.txt (one line on PASS; one line per failing beat on FAIL) and gates
# regeneration on the EXIT CODE: 0 PASS, 1 FAIL, 2 ERROR(no sidecar).
# Artifacts left on disk for drill-down: words.json, qa_audio.json, qa_visual.json, sig.log, audio.wav.
set -uo pipefail
VID="${1:?usage: review.sh <video.mp4> [beats.json]}"
BEATS="${2:-${VID%.*}.beats.json}"
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="$(cd "$(dirname "$VID")" && pwd)"
VIDABS="$WORK/$(basename "$VID")"
[ -f "$BEATS" ] || BEATS="$WORK/$(basename "$BEATS")"
cd "$WORK"

if [ ! -f "$BEATS" ]; then
  echo "VERDICT: ERROR  no beats.json sidecar ('$BEATS') - rebuild with a sidecar-emitting builder (vid.py emits <name>.beats.json)" | tee review.txt
  exit 2
fi
source "$HERE/stt-env.sh" 2>/dev/null || true
NB=$(python3 -c "import json;d=json.load(open(r'$BEATS'));print(len(d['beats'] if isinstance(d,dict) else d))" 2>/dev/null || echo "?")
FAIL=0; LINES=""

# 1. structural sanity
HASA=$(ffprobe -v error -select_streams a -show_entries stream=codec_type -of csv=p=0 "$VIDABS" 2>/dev/null)
[ -z "$HASA" ] && { FAIL=1; LINES="$LINES"$'\n'"  structural: no audio stream"; }

# 2. audio signal: loudness / clipping / grossly-long silence (one ffmpeg pass)
ffmpeg -hide_banner -nostats -i "$VIDABS" -af "silencedetect=n=-40dB:d=2.5,ebur128=peak=true,volumedetect" -f null - 2>sig.log || true
OUT=$(python3 "$HERE/qa_signal.py" sig.log); RC=$?
[ $RC -ne 0 ] && { FAIL=1; LINES="$LINES"$'\n'"$OUT"; }

# 3. transcribe narration to word-timestamped JSON
ffmpeg -y -v error -i "$VIDABS" -vn -ac 1 -ar 16000 audio.wav
python3 "$HERE/transcribe.py" audio.wav words.json

# 4. narration sync / spillover / content / pronunciation (keyed off beats.json)
OUT=$(python3 "$HERE/qa_audio.py" words.json "$BEATS"); RC=$?
[ $RC -ne 0 ] && { FAIL=1; LINES="$LINES"$'\n'"$OUT"; }

# 5. visual OCR: blank / wrong / scroll-incomplete (only beats that declare expected_onscreen)
OUT=$(python3 "$HERE/qa_visual.py" "$VIDABS" "$BEATS"); RC=$?
[ $RC -ne 0 ] && { FAIL=1; LINES="$LINES"$'\n'"$OUT"; }

if [ "$FAIL" -eq 0 ]; then
  echo "VERDICT: PASS ($NB beats, 0 issues)" | tee review.txt
  exit 0
fi
{ echo "VERDICT: FAIL"; printf '%b\n' "$LINES" | sed '/^[[:space:]]*$/d'; } | tee review.txt
exit 1
