#!/usr/bin/env python3
"""OCR the rendered frames at each beat's content moment and assert the expected on-screen
tokens are present. Catches blank / wrong / scroll-incomplete visuals that audio checks can't.

Only beats that declare expected_onscreen are checked (others are skipped). For scrolled-file
beats, declare scroll_top tokens (first lines of the file) to verify the top was actually shown.

Usage: python3 qa_visual.py video.mp4 beats.json
Env: QA_OCR_MINCONF unused (psm6 text only). Writes qa_visual.json. Exit 1 on any issue.
"""
import json, os, re, subprocess, sys, tempfile

PSM = os.environ.get("QA_OCR_PSM", "6")
MINCHARS = int(os.environ.get("QA_MIN_OCR", "12"))  # a result beat below this is near-blank (e.g.
                                                    # frozen on a command being typed, not the content)

def ocr_at(video, t):
    f = tempfile.mktemp(suffix=".png")
    try:
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", str(t), "-i", video, "-frames:v", "1",
                        "-vf", "negate,format=gray,eq=contrast=1.6,scale=iw*2:ih*2", "-y", f],
                       check=True)
        txt = subprocess.check_output(["tesseract", f, "stdout", "--psm", PSM],
                                      stderr=subprocess.DEVNULL).decode("utf-8", "ignore")
    except Exception:
        txt = ""
    finally:
        if os.path.exists(f):
            os.unlink(f)
    return txt

def nrm(s):
    # collapse underscores/hyphens/punctuation/whitespace so OCR "delete orders" matches
    # the expected token "delete_orders"
    return re.sub(r'[^a-z0-9]+', ' ', s.lower())

def beat_text(video, start, end):
    # sample several frames across the beat and union their OCR. A single-frame check misfires
    # on scrolling beats (a token is only on screen briefly); the union catches a token shown
    # at ANY point. Returns (normalized union text, max meaningful chars in any single frame).
    lo, hi = start + 0.8, max(start + 0.9, end - 0.8)
    times = [lo + (hi - lo) * k / 4 for k in range(5)] if hi > lo else [start + 0.5]
    frames = [ocr_at(video, t) for t in times]
    union = nrm(" ".join(frames))
    maxchars = max((len(re.sub(r'[^a-z0-9]', '', f)) for f in frames), default=0)
    return union, maxchars

def main():
    video, beats_path = sys.argv[1], sys.argv[2]
    B = json.load(open(beats_path, encoding="utf-8"))
    beats = B["beats"] if isinstance(B, dict) else B
    flags = []
    any_exp = False
    for beat in beats:
        # check every RESULT beat (where content should be on screen). Even with no declared
        # expectations we run a near-blank check, so a freeze frozen on the wrong frame (e.g. a
        # command being typed) cannot pass silently.
        if beat.get("kind") not in (None, "result"):
            continue
        exp = beat.get("expected_onscreen") or []
        scroll_top = beat.get("scroll_top") or []
        any_exp = any_exp or bool(exp) or bool(scroll_top)
        start = float(beat["narr_start_s"])
        end = float(beat.get("beat_end_s", start + 3))
        issues = []
        union, maxchars = beat_text(video, start, end)
        if maxchars < MINCHARS:
            issues.append(f"sparse_visual ('{union.strip()[:34]}' - result frames nearly empty)")
        elif exp:
            missing = [t for t in exp if nrm(t).strip() not in union]
            if missing:
                issues.append("wrong_visual missing=" + ",".join(missing[:4]))
        if scroll_top:
            ttxt = nrm(ocr_at(video, start + 1.0))
            tmiss = [t for t in scroll_top if nrm(t).strip() not in ttxt]
            if tmiss:
                issues.append("scroll_incomplete top_missing=" + ",".join(tmiss[:3]))
        if issues:
            flags.append({"beat": beat["id"], "t": round((start + end) / 2.0, 1), "issues": issues})
    json.dump({"flags": flags}, open(os.environ.get("QA_VISUAL_OUT", "qa_visual.json"), "w"))
    for f in flags:
        print(f"  {f['beat']} @{f['t']}s " + " | ".join(f["issues"]))
    if not any_exp:
        print("  note: no expected_onscreen declared - ran near-blank check only; add tokens for full visual matching")
    sys.exit(1 if flags else 0)

if __name__ == "__main__":
    main()
