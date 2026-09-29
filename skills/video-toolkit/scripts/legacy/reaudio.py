import subprocess, os, sys, json, tempfile, shutil
# reaudio.py <spec.json> <existing_video.mp4> <out.mp4>
# Rebuilds the narration audio with an English-locked voice (no code-switching),
# placed on the EXACT original timeline (old voice is byte-deterministic, so re-
# synthing it reproduces the original slot durations), then muxes onto the
# untouched video stream (copy, no re-encode). Picture is preserved bit-for-bit.
OLD = "en-US-AvaMultilingualNeural"   # what the videos were built with (code-switches on coined words)
NEW = "en-US-AvaNeural"               # same Ava persona, English-only -> cannot switch language
GAP = 0.4

spec_path, video_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
spec = json.load(open(spec_path, encoding="utf-8"))
TMP = tempfile.mkdtemp(prefix="reaud_")

def dur(p):
    return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration",
        "-of","default=noprint_wrappers=1:nokey=1", p]).decode().strip())
def tts(voice, text, out):
    subprocess.run(["python","-m","edge_tts","--voice",voice,"--text",text,"--write-media",out],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

auds = []; cum = 0.0; max_atempo = 1.0
for i, b in enumerate(spec["beats"]):
    for tag in ("a","b"):
        old = f"{TMP}/{i}{tag}o.mp3"; tts(OLD, b[tag], old); ld_old = dur(old)   # original slot length
        new = f"{TMP}/{i}{tag}n.mp3"; tts(NEW, b[tag], new); ld_new = dur(new)
        use = new
        # Only time-fit if the English clip would overrun its slot (rare; monolingual is ~equal/shorter).
        if ld_new > ld_old + 0.35:
            factor = round(ld_new / (ld_old + 0.30), 4)
            max_atempo = max(max_atempo, factor)
            fit = f"{TMP}/{i}{tag}f.mp3"
            subprocess.run(["ffmpeg","-v","error","-i",new,"-filter:a",f"atempo={factor}","-y",fit], check=True)
            use = fit
        auds.append((use, round(cum + 0.1, 3)))
        cum += ld_old + GAP

inp = ["-i", video_path]
fc = ""; mr = ""
for j,(mp3,st) in enumerate(auds):
    inp += ["-i", mp3]
    fc += f"[{j+1}:a]adelay={int(st*1000)}:all=1[a{j}];"; mr += f"[a{j}]"
fc += (f"{mr}amix=inputs={len(auds)}:duration=longest:normalize=0[m];"
       f"[m]loudnorm=I=-17:TP=-2:LRA=11,aresample=48000[ao]")
subprocess.run(["ffmpeg","-v","error"] + inp + ["-filter_complex", fc,
    "-map","0:v","-c:v","copy","-map","[ao]","-c:a","aac","-b:a","192k","-ar","48000","-ac","2",
    "-shortest","-y", out_path], check=True)

shutil.rmtree(TMP, ignore_errors=True)
print(f"REAUDIO {spec['name']}: {len(auds)} clips, {cum:.1f}s, max_atempo={max_atempo:.3f} -> {out_path}")
