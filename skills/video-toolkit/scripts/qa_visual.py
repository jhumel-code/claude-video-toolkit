#!/usr/bin/env python3
"""OCR the rendered frames at each beat's content moment and assert the expected on-screen
tokens are present. Catches blank / wrong / scroll-incomplete visuals that audio checks can't.

Only beats that declare expected_onscreen are checked (others are skipped). For scrolled-file
beats, declare scroll_top tokens (first lines of the file) to verify the top was actually shown.

Usage: python3 qa_visual.py video.mp4 beats.json
Env: QA_OCR_MINCONF unused (psm6 text only). Writes qa_visual.json. Exit 1 on any issue.
"""
import json, os, subprocess, sys, tempfile

PSM = os.environ.get("QA_OCR_PSM", "6")

def ocr_at(video, t):
    f = tempfile.mktemp(suffix=".png")
    try:
        subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", video, "-frames:v", "1",
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

def main():
    video, beats_path = sys.argv[1], sys.argv[2]
    B = json.load(open(beats_path, encoding="utf-8"))
    beats = B["beats"] if isinstance(B, dict) else B
    flags = []
    for i, beat in enumerate(beats):
        exp = beat.get("expected_onscreen") or []
        scroll_top = beat.get("scroll_top") or []
        if not exp and not scroll_top:
            continue
        start = float(beat["narr_start_s"])
        end = float(beat.get("beat_end_s", start + 3))
        mid = (start + end) / 2.0
        issues = []
        if exp:
            txt = ocr_at(video, mid).lower()
            if len(txt.strip()) < 3:
                issues.append("blank_visual")
            else:
                missing = [t for t in exp if t.lower() not in txt]
                if missing:
                    issues.append("wrong_visual missing=" + ",".join(missing[:4]))
        if scroll_top:
            ttxt = ocr_at(video, start + 1.0).lower()
            tmiss = [t for t in scroll_top if t.lower() not in ttxt]
            if tmiss:
                issues.append("scroll_incomplete top_missing=" + ",".join(tmiss[:3]))
        if issues:
            flags.append({"beat": beat["id"], "t": round(mid, 1), "issues": issues})
    json.dump({"flags": flags}, open(os.environ.get("QA_VISUAL_OUT", "qa_visual.json"), "w"))
    for f in flags:
        print(f"  {f['beat']} @{f['t']}s " + " | ".join(f["issues"]))
    sys.exit(1 if flags else 0)

if __name__ == "__main__":
    main()
