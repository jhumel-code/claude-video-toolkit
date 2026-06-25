#!/usr/bin/env python3
"""Parse one ffmpeg pass log (silencedetect + ebur128 + volumedetect) -> audio-quality flags.
We deliberately do NOT use freezedetect/blackdetect: this pipeline freezes frames on purpose
(holds, scroll tails), so those would false-positive. Blank visuals are caught by qa_visual
(OCR). Here we only judge global audio quality + grossly-long silence.

Usage: python3 qa_signal.py sig.log
Env: QA_LUFS_LO(-19) QA_LUFS_HI(-15) QA_CLIP(-0.1 dB) QA_LONG_SILENCE(4.0 s)
"""
import os, re, sys

LUFS_LO = float(os.environ.get("QA_LUFS_LO", "-19"))
LUFS_HI = float(os.environ.get("QA_LUFS_HI", "-15"))
CLIP    = float(os.environ.get("QA_CLIP", "-0.1"))
LONGSIL = float(os.environ.get("QA_LONG_SILENCE", "4.0"))

def main():
    log = open(sys.argv[1], encoding="utf-8", errors="ignore").read()
    fails, notes = [], []
    # long silence is usually an intentional scroll/hold tail -> soft note, never a FAIL
    for m in re.finditer(r'silence_start:\s*([\d.]+)[\s\S]*?silence_duration:\s*([\d.]+)', log):
        st, d = float(m.group(1)), float(m.group(2))
        if d > LONGSIL:
            notes.append(f"long_silence {d:.1f}s @{st:.1f}s (check it is an intended scroll/hold)")
    # ebur128 prints momentary I: throughout; the LAST one is the Summary integrated loudness
    iss = re.findall(r'\bI:\s*(-?[\d.]+)\s*LUFS', log)
    if iss:
        i = float(iss[-1])
        if not (LUFS_LO <= i <= LUFS_HI):
            fails.append(f"loudness I={i} LUFS (target ~-17)")
    mv = re.search(r'max_volume:\s*(-?[\d.]+)\s*dB', log)
    if mv and float(mv.group(1)) >= CLIP:
        fails.append(f"clipping max_volume={mv.group(1)} dB")
    for x in fails:
        print(f"  signal: {x}")
    for x in notes:
        print(f"  note: {x}")
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
