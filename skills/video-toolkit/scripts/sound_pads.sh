#!/usr/bin/env bash
# sound_pads.sh - richer FREE, deterministic music beds + SFX.
#   Pads via ffmpeg aevalsrc (stacked harmonics + attack/release + lowpass warmth).
#   Riser/blip via sox Karplus-Strong (pl). See docs/10-style-guide.md S8.
# Usage:  bash sound_pads.sh [outdir]
set -euo pipefail
OUT="${1:-.}"; SR=48000; mkdir -p "$OUT"
ff(){ ffmpeg -v error -y "$@"; }
# Am pad (A2 E3 A3 C4): attack (1-exp) + release (exp tail) + lowpass
ff -f lavfi -i "aevalsrc='0.07*(sin(2*PI*110*t)+sin(2*PI*164.81*t)+sin(2*PI*220*t)+sin(2*PI*261.63*t))*(1-exp(-t/0.4))*exp(-max(t-6,0)/1.5)':d=8:s=${SR},lowpass=f=900:poles=2" -ac 2 "$OUT/pad_Am.wav"
# Dm resolution pad (D3 A3 D4 F4)
ff -f lavfi -i "aevalsrc='0.07*(sin(2*PI*146.83*t)+sin(2*PI*220*t)+sin(2*PI*293.66*t)+sin(2*PI*349.23*t))*(1-exp(-t/0.5))*exp(-max(t-5,0)/1.5)':d=7:s=${SR},lowpass=f=800:poles=2" -ac 2 "$OUT/pad_Dm.wav"
echo "pads -> $OUT/pad_Am.wav $OUT/pad_Dm.wav"
if command -v sox >/dev/null 2>&1; then
  sox -n -r $SR -b 16 "$OUT/blip.wav" synth pl A4 remix - fade 0 0.4 .05 norm -1
  echo "sfx  -> $OUT/blip.wav"
else
  echo "(sox not installed - install for risers/blips: sudo apt-get install sox)"
fi
