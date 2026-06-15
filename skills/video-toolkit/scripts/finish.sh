#!/usr/bin/env bash
# finish.sh - deterministic finishing pass for the Claude Video Toolkit.
#   deband+dither (fixes dark-gradient banding) -> optional brand grade ->
#   subtle film-grain + vignette -> bit-exact single-thread x264 encode.
#   See docs/10-style-guide.md and docs/09-improvement-plan.md.
#
# Usage:  bash finish.sh <in.mp4> [out.mp4] [mode]
#   mode = brand (default) -> applies a color grade (brand-tunable via $GRADE)
#        = demo            -> deband + light grain only; preserves terminal theme
#
# Use a profile's grade:
#   GRADE="$(python3 scripts/brand_config.py grade <profile>)" bash finish.sh in.mp4 out.mp4 brand
# DRYRUN=1 prints the filter chain without encoding.
set -euo pipefail
IN="${1:?usage: bash finish.sh <in.mp4> [out.mp4] [mode]}"
OUT="${2:-${IN%.*}_finished.mp4}"
MODE="${3:-brand}"
CRF=18
DEBAND="deband=1thr=0.02:2thr=0.02:3thr=0.02:4thr=0.02:range=12:blur=1"
DEFAULT_GRADE="curves=r='0/0 0.5/0.48 1/1':g='0/0 0.5/0.51 1/1':b='0/0 0.5/0.56 1/1',eq=contrast=1.06:brightness=-0.02:saturation=0.92,colorbalance=bs=0.05:bh=0.03"
if [ "$MODE" = "demo" ]; then
  GRADE=""; GRAIN=4; VIG="PI/6"
else
  GRADE="${GRADE:-$DEFAULT_GRADE}"; GRAIN=6; VIG="PI/5"
fi
VF="${DEBAND},noise=c0s=${GRAIN}:c0f=t+u,${GRADE:+${GRADE},}vignette=${VIG},format=yuv420p"
if [ "${DRYRUN:-0}" = "1" ]; then echo "VF=$VF"; exit 0; fi
HASAUDIO=$(ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "$IN" 2>/dev/null | head -1 || true)
AOPT=(); [ -n "$HASAUDIO" ] && AOPT=(-c:a copy)
ffmpeg -v error -y -i "$IN" -vf "$VF" \
  -threads 1 -fflags +bitexact \
  -c:v libx264 -x264-params "threads=1:sliced-threads=0" \
  -preset slow -crf "$CRF" -pix_fmt yuv420p \
  "${AOPT[@]}" "$OUT"
echo "finished ($MODE) -> $OUT  ($(stat -c%s "$OUT") bytes)"
