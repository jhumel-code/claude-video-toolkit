#!/usr/bin/env python3
"""assemble.py <body.mp4> <out.mp4> [--intro auto|none|<clip>] [--outro <clip>]

Joins bookends onto a narrated body in ONE encode, at the body's canvas and frame rate.
--intro auto (the default) uses the brand profile's official `intro_clip` (BRAND_PROFILE),
so a brand that has an official intro never gets a generated one; a brand without one gets
no intro unless you pass a clip (e.g. from brand_intro.py). Parts that differ in size are
scaled to fit and padded with the brand's terminal margin colour; parts without audio get
silence. Run scripts/review.sh on the BODY first, and finish.sh on the joined result.
"""
import argparse, os, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from brand_config import load_profile
from narrate import dur

ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
ap.add_argument("body")
ap.add_argument("out")
ap.add_argument("--intro", default="auto")
ap.add_argument("--outro")
args = ap.parse_args()

prof = load_profile()
intro = None
if args.intro == "auto":
    if prof.get("intro_clip"):
        intro = prof["abs"]("intro_clip")
elif args.intro != "none":
    intro = args.intro
parts = [p for p in (intro, args.body, args.outro) if p]
for p in parts:
    if not os.path.exists(p):
        sys.exit(f"not found: {p}")


def probe(p, entries, stream="v:0"):
    return subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", stream, "-show_entries",
                                    entries, "-of", "csv=p=0", p]).decode().strip()


W, H = (int(v) for v in probe(args.body, "stream=width,height").split(","))
FPS = probe(args.body, "stream=r_frame_rate")
pad = (prof.get("terminal", {}).get("margin_fill") or "#000000").replace("#", "0x")

inputs, fc, cat = [], "", ""
for p in parts:
    inputs += ["-i", p]
n_in = len(parts)
for i, p in enumerate(parts):
    fc += (f"[{i}:v]scale={W}:{H}:force_original_aspect_ratio=decrease:flags=lanczos,"
           f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color={pad},fps={FPS},format=yuv420p,setsar=1[v{i}];")
    if probe(p, "stream=index", "a"):
        fc += f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo[a{i}];"
    else:   # a silent part gets a silence input of its own length
        inputs += ["-f", "lavfi", "-t", f"{dur(p):.3f}", "-i", "anullsrc=r=48000:cl=stereo"]
        fc += f"[{n_in}:a]anull[a{i}];"
        n_in += 1
    cat += f"[v{i}][a{i}]"
fc += f"{cat}concat=n={len(parts)}:v=1:a=1[v][a]"
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", *inputs, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
                "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-y", args.out], check=True)
offset = dur(intro) if intro else 0.0
print(f"joined {' + '.join(os.path.basename(p) for p in parts)} -> {args.out} "
      f"({dur(args.out):.2f}s, {W}x{H}); the body starts at {offset:.2f}s")
