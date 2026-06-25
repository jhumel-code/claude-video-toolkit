#!/usr/bin/env python3
"""faster-whisper -> compact word-timestamped JSON. Deterministic (fixed beam, temp 0).

Usage: python3 transcribe.py audio.wav [words.json]
Env: STT_MODEL (default small.en), STT_DEVICE (cuda|cpu), STT_COMPUTE (int8_float16|int8).
Falls back to CPU int8 if CUDA/cuDNN is unavailable (the #1 WSL gotcha).
Output schema: {language, duration, model, segments:[{start,end,text,words:[{w,s,e,p}]}]}
"""
import json, os, sys

def main():
    audio = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else None
    model = os.environ.get("STT_MODEL", "small.en")
    device = os.environ.get("STT_DEVICE", "cuda")
    compute = os.environ.get("STT_COMPUTE", "int8_float16" if device == "cuda" else "int8")
    from faster_whisper import WhisperModel

    def run(dev, comp):
        # CUDA errors (missing libcublas/libcudnn) often surface only when the lazy segment
        # generator is consumed (encode), so materialize the list INSIDE the try.
        m = WhisperModel(model, device=dev, compute_type=comp)
        segs, inf = m.transcribe(audio, word_timestamps=True, vad_filter=True,
                                 beam_size=5, temperature=0.0)
        rows = []
        for s in segs:
            ws = [{"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2),
                   "p": round(w.probability, 3)} for w in (s.words or [])]
            rows.append({"start": round(s.start, 2), "end": round(s.end, 2),
                         "text": s.text.strip(), "words": ws})
        return rows, inf

    try:
        out_segs, info = run(device, compute)
    except Exception as e:
        sys.stderr.write(f"[transcribe] {device}/{compute} failed ({e}); CPU int8 fallback\n")
        out_segs, info = run("cpu", "int8")
    doc = {"language": info.language, "duration": round(info.duration, 2),
           "model": model, "segments": out_segs}
    js = json.dumps(doc, ensure_ascii=False)
    if out:
        open(out, "w", encoding="utf-8").write(js)
        sys.stderr.write(f"[transcribe] {len(out_segs)} segments, "
                         f"{sum(len(s['words']) for s in out_segs)} words -> {out}\n")
    else:
        print(js)

if __name__ == "__main__":
    main()
