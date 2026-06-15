import subprocess, os, sys
P = sys.argv[1]   # voice prefix, e.g. "andrew"
WD = os.environ.get("WORKDIR", ".").rstrip("/")
SRC = os.environ.get("SRC", WD + "/source.mp4")
TMP = f"{WD}/_intro_{P}"
os.makedirs(TMP, exist_ok=True)
GAP = 0.4

def dur(p):
    return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration",
        "-of","default=noprint_wrappers=1:nokey=1", p]).decode().strip())

# (clip, beat time in SRC, src_cap, available-footage-before-next-content)
# r01a EXECUTES the help cmd mid-intro (type->Enter->output ~4.5) then freezes output.
PLAN = [
 ("r01a", 1.0, 5.5, 4.5 + 100),   # cap 5.5 so it plays through output, freeze the rest
 ("r01b", 5.5, 99.0, 17.0 - 5.5), # hold output until scan typing begins (~17.0)
 ("r01c", 17.0, 99.0, 22.9 - 17.0),
]

clip_files = []; starts = {}; cum = 0.0
for cid, bt, cap, avail in PLAN:
    ld = dur(f"{WD}/vo/{P}_{cid}.mp3")
    clip_dur = ld + GAP
    src_len = max(0.4, min(clip_dur, cap, avail - 0.12))
    freeze = round(clip_dur - src_len, 3)
    out = f"{TMP}/{cid}.mp4"
    vf = f"tpad=stop_mode=clone:stop_duration={freeze}" if freeze > 0.02 else "null"
    subprocess.run(["ffmpeg","-v","error","-ss",f"{bt}","-t",f"{src_len}","-i",SRC,
        "-an","-vf",vf,"-r","25","-c:v","libx264","-crf","18","-preset","medium","-pix_fmt","yuv420p",
        "-y",out],check=True)
    clip_files.append(out)
    starts[cid] = round(cum + 0.10, 3)
    cum += clip_dur

with open(f"{TMP}/list.txt","w") as f:
    for cf in clip_files: f.write(f"file '{cf}'\n")
subprocess.run(["ffmpeg","-v","error","-f","concat","-safe","0","-i",f"{TMP}/list.txt",
    "-c","copy","-y",f"{WD}/intro-silent-{P}.mp4"],check=True)
print("INTRO_%s %.2fs" % (P, cum))
print("STARTS_MS=" + " ".join(f"{c}:{int(starts[c]*1000)}" for c,_,_,_ in PLAN))
