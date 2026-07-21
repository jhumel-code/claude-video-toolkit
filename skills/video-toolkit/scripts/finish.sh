#!/usr/bin/env bash
# finish.sh - deterministic finishing pass for the Claude Video Toolkit.
#   [optional upscale] -> deband+dither (fixes dark-gradient banding) ->
#   optional film-grain -> optional brand grade -> optional vignette ->
#   bit-exact single-thread x264 encode.
#   See docs/10-style-guide.md and docs/09-improvement-plan.md.
#
# Usage:  bash finish.sh <in.mp4> [out.mp4] [mode]
#   mode = brand (default) -> color grade + light grain + soft vignette
#          (brand-tunable via $GRADE; see brand_config.py grade <profile>)
#        = demo            -> deband only by default. Crystal-clear, no
#          grain/vignette/grade — a security/audit tool's demo footage should
#          read as unstaged, not stylized (default as of 2026-07-21, set from
#          the OpenShell policy-prover demo after the user rejected grain and
#          vignette on narrated terminal footage). Pass GRAIN=N / VIG=PI/xx /
#          GRADE="..." explicitly to opt back into texture for a specific demo.
#
# Use a profile's grade:
#   GRADE="$(python3 scripts/brand_config.py grade <profile>)" bash finish.sh in.mp4 out.mp4 brand
#
# SCALE="WxH" upscales BEFORE anything else (e.g. SCALE=3840x2160 for a
# 2560x1440 source). ORDER MATTERS: scaling AFTER deband/grade aliases the
# grade's sub-pixel dither into a visible periodic band pattern on flat
# backgrounds — invisible at native res, clearly visible post-upscale. Always
# scale first. Confirmed empirically 2026-07-21 via native-resolution pixel
# crops (raw source clean, each filter clean in isolation, grade-then-scale
# banded, scale-then-grade clean) — see references/07-environment-and-gotchas.md.
#
# DRYRUN=1 prints the filter chain without encoding.
set -euo pipefail
IN="${1:?usage: bash finish.sh <in.mp4> [out.mp4] [mode]}"
OUT="${2:-${IN%.*}_finished.mp4}"
MODE="${3:-brand}"
CRF=18
DEBAND="deband=1thr=0.02:2thr=0.02:3thr=0.02:4thr=0.02:range=12:blur=1"
# Default grade LIFTS midtones (curves > 0.5) and adds positive brightness so
# the finishing pass never darkens the source. ffmpeg's vignette filter's
# "angle" runs the OPPOSITE way from intuition: a SMALLER angle = a SOFTER,
# lighter falloff; a LARGER angle (approaching its PI/2 clip) crushes the
# corners toward black. Verified empirically 2026-07-21 (PI/2.8 was nearly
# black outside a small center hotspot; PI/16 read clean and undarkened) —
# do not "soften" this by raising the number. Override GRADE/VIG/GRAIN via env.
DEFAULT_GRADE="curves=r='0/0 0.5/0.54 1/1':g='0/0 0.5/0.55 1/1':b='0/0 0.5/0.6 1/1',eq=contrast=1.02:brightness=0.04:saturation=1.0,colorbalance=bs=0.04:bh=0.02"
if [ "$MODE" = "demo" ]; then
  GRADE="${GRADE:-}"; GRAIN="${GRAIN:-0}"; VIG="${VIG:-}"
else
  GRADE="${GRADE:-$DEFAULT_GRADE}"; GRAIN="${GRAIN:-6}"; VIG="${VIG:-PI/16}"
fi

# Build the chain from parts and skip empty ones, so an empty GRADE/VIG/GRAIN
# (crystal-clear demo mode) doesn't leave a stray/malformed filter behind, and
# SCALE — when set — always lands first, before anything that could alias.
STEPS=()
[ -n "${SCALE:-}" ] && STEPS+=("scale=${SCALE}:flags=lanczos")
STEPS+=("$DEBAND")
[ -n "$GRAIN" ] && [ "$GRAIN" != "0" ] && STEPS+=("noise=c0s=${GRAIN}:c0f=t+u")
[ -n "$GRADE" ] && STEPS+=("$GRADE")
[ -n "$VIG" ] && STEPS+=("vignette=${VIG}")
STEPS+=("format=yuv420p")
VF=$(IFS=,; echo "${STEPS[*]}")

if [ "${DRYRUN:-0}" = "1" ]; then echo "VF=$VF"; exit 0; fi
HASAUDIO=$(ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "$IN" 2>/dev/null | head -1 || true)
AOPT=(); [ -n "$HASAUDIO" ] && AOPT=(-c:a copy)
# Default encode is bit-exact single-thread (deterministic). FAST=1 uses a
# multithreaded medium preset for large 4K/60 renders (not bit-exact) so a
# high-resolution finishing pass completes in reasonable time.
if [ "${FAST:-0}" = "1" ]; then
  ffmpeg -v error -y -i "$IN" -vf "$VF" \
    -c:v libx264 -preset medium -crf "$CRF" -pix_fmt yuv420p \
    "${AOPT[@]}" "$OUT"
else
  ffmpeg -v error -y -i "$IN" -vf "$VF" \
    -threads 1 -fflags +bitexact \
    -c:v libx264 -x264-params "threads=1:sliced-threads=0" \
    -preset slow -crf "$CRF" -pix_fmt yuv420p \
    "${AOPT[@]}" "$OUT"
fi
echo "finished ($MODE) -> $OUT  ($(stat -c%s "$OUT") bytes)"
