#!/usr/bin/env python3
"""Join faster-whisper words.json + <video>.beats.json -> per-beat audio/sync flags.

This is the check that catches the bugs frame-extraction missed: narration drifting from its
visual, and a narration spilling past the next beat (double-voiceover). It keys off the
beats.json sidecar so there is NO timeline reverse-engineering.

Usage: python3 qa_audio.py words.json beats.json
Flags: drift, overrun(spillover), content_mismatch, pron_suspect, dead_air.
Exit 1 if any beat has issues. Writes qa_audio.json.
Env: QA_SYNC(1.0) QA_OVERRUN(0.4) QA_RATIO(0.55) QA_PWORD(0.4) QA_DEADAIR(2.5)
"""
import json, os, re, sys
from difflib import SequenceMatcher

SYNC    = float(os.environ.get("QA_SYNC", "1.0"))
OVERRUN = float(os.environ.get("QA_OVERRUN", "0.7"))   # > whisper word-timestamp noise (~200ms) + GAP
RATIO   = float(os.environ.get("QA_RATIO", "0.55"))
PWORD   = float(os.environ.get("QA_PWORD", "0.4"))
DEADAIR = float(os.environ.get("QA_DEADAIR", "2.5"))

def norm(s):
    return re.sub(r'[^a-z0-9 ]', ' ', s.lower()).split()

def main():
    W = json.load(open(sys.argv[1], encoding="utf-8"))
    B = json.load(open(sys.argv[2], encoding="utf-8"))
    beats = B["beats"] if isinstance(B, dict) else B
    words = [w for s in W["segments"] for w in s["words"]]

    flags = []
    for i, beat in enumerate(beats):
        start = float(beat["narr_start_s"])
        # bound the last beat's window to its own clip (+0.5s) so it doesn't swallow trailing
        # outro/credits audio and false-flag content_mismatch.
        nxt = (float(beats[i + 1]["narr_start_s"]) if i + 1 < len(beats)
               else float(beat.get("beat_end_s", start + 6)) + 0.5)
        win = [w for w in words if start - 0.25 <= w["s"] < nxt]
        issues = []
        heard = " ".join(w["w"].strip() for w in win).strip()
        if win:
            hstart, hend = win[0]["s"], win[-1]["e"]
            if hstart - start > SYNC:
                issues.append(f"drift=+{round(hstart - start, 1)}s")
            if hend - nxt > OVERRUN:
                issues.append(f"overrun=+{round(hend - nxt, 1)}s")
            # dead air only matters on a STATIC beat. On a scroll/play-through beat the screen
            # is moving during any silence, so a silent stretch there is intended, not dead air.
            if not beat.get("play_b"):
                for a, b in zip(win, win[1:]):
                    if b["s"] - a["e"] > DEADAIR:
                        issues.append(f"dead_air={round(b['s'] - a['e'], 1)}s")
                        break
        elif norm(beat.get("narr_text", "")):
            issues.append("no_speech_in_window")
        ratio = SequenceMatcher(None, norm(heard), norm(beat.get("narr_text", ""))).ratio()
        if len(norm(beat.get("narr_text", ""))) >= 4 and ratio < RATIO:
            issues.append(f"content_mismatch ratio={round(ratio, 2)}")
        # pronunciation is a SOFT NOTE only (ASR can silently auto-correct, so this is a hint
        # for a human spot-listen, never a hard FAIL). Flag a jargon term only if NONE of its
        # significant tokens were transcribed at all - i.e. whisper could not hear it cleanly.
        notes = []
        htoks = set(norm(heard))
        for term in beat.get("jargon", []):
            cand = {t for t in norm(term) if len(t) >= 3}
            if cand and not (cand & htoks):
                notes.append(f"pron_suspect '{term}' (not heard cleanly - spot-listen)")
        flags.append({"beat": beat["id"], "t": round(start, 1), "issues": issues, "notes": notes,
                      "ratio": round(ratio, 2), "heard": heard[:90]})

    json.dump({"flags": flags}, open(os.environ.get("QA_AUDIO_OUT", "qa_audio.json"), "w"),
              ensure_ascii=False)
    fails = [f for f in flags if f["issues"]]
    for f in fails:
        tail = f' | heard:"{f["heard"]}"' if any(
            k in i for i in f["issues"] for k in ("mismatch", "drift", "overrun", "no_speech")) else ""
        print(f"  {f['beat']} @{f['t']}s " + " | ".join(f["issues"]) + tail)
    for f in flags:
        for n in f["notes"]:
            print(f"  note: {f['beat']} @{f['t']}s {n}")
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
