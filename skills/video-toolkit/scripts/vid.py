import subprocess, os, sys, json
# vid.py <spec.json>  -> <name>.mp4  (two-phase pacing: command typed under intent line, result under explanation)
# Also emits <name>.beats.json (the sidecar scripts/review.sh keys off to self-review the render),
# and applies profiles/pronounce.json to narration before edge-tts (jargon pronunciation).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from pronounce import normalize as _pron, jargon_in as _jarg
except Exception:
    _pron = lambda t: t; _jarg = lambda t: []
spec = json.load(open(sys.argv[1], encoding="utf-8"))
name = spec["name"]
base = os.environ.get("WORKDIR", ".").rstrip("/") + "/"
SRC  = base + spec["footage"]
V    = spec.get("voice", "en-US-AvaNeural")
OUTDIR = spec.get("outdir", base)
TMP  = base + f"_v_{name}"; os.makedirs(TMP, exist_ok=True)
GAP  = 0.4
def dur(p): return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",p]).decode().strip())
def tts(text,out): subprocess.run(["python","-m","edge_tts","--voice",V,"--text",_pron(text),"--write-media",out],check=True)
def seg(bt,src_len,freeze,out):
    vf = f"tpad=stop_mode=clone:stop_duration={freeze}" if freeze>0.02 else "null"
    subprocess.run(["ffmpeg","-v","error","-ss",f"{bt}","-t",f"{src_len}","-i",SRC,"-an","-vf",vf,"-r","25",
        "-c:v","libx264","-crf","18","-preset","medium","-pix_fmt","yuv420p","-y",out],check=True)

clips=[]; auds=[]; cum=0.0; meta=[]
for i,b in enumerate(spec["beats"]):
    ts=float(b["ts"]); res=float(b["res"])
    aMp3=f"{TMP}/{i}a.mp3"; bMp3=f"{TMP}/{i}b.mp3"
    tts(b["a"],aMp3); tts(b["b"],bMp3)
    ldA=dur(aMp3); ldB=dur(bMp3)
    aclip=ldA+GAP; avail=(res-0.1)-ts; src_a=max(0.4,min(aclip,avail))
    outA=f"{TMP}/{i}a.mp4"; seg(ts,src_a,round(aclip-src_a,3),outA)
    # audio at the ACTUAL measured clip boundary so narration can never drift from video
    a_at=round(cum+0.1,3); clips.append(outA); auds.append((aMp3,a_at)); cum+=dur(outA)
    meta.append({"id":f"b{i}a","kind":"intent","narr_start_s":a_at,"narr_text":b["a"],
                 "beat_end_s":round(cum,3),"jargon":_jarg(b["a"]),"expected_onscreen":b.get("expect_a",[])})
    bclip=ldB+GAP; src_b=max(0.4,min(bclip,1.5))
    outB=f"{TMP}/{i}b.mp4"; seg(res,src_b,round(bclip-src_b,3),outB)
    b_at=round(cum+0.1,3); clips.append(outB); auds.append((bMp3,b_at)); cum+=dur(outB)
    meta.append({"id":f"b{i}b","kind":"result","narr_start_s":b_at,"narr_text":b["b"],
                 "beat_end_s":round(cum,3),"jargon":_jarg(b["b"]),"expected_onscreen":b.get("expect",[]),
                 "scroll_top":b.get("scroll_top",[])})
json.dump({"beats":meta}, open(OUTDIR+f"{name}.beats.json","w"), ensure_ascii=False, indent=1)

with open(f"{TMP}/list.txt","w") as fp:
    for c in clips: fp.write(f"file '{c}'\n")
silent=f"{TMP}/silent.mp4"
subprocess.run(["ffmpeg","-v","error","-f","concat","-safe","0","-i",f"{TMP}/list.txt","-c","copy","-y",silent],check=True)

inp=["-i",silent]; fc=""; mr=""
for j,(mp3,st) in enumerate(auds):
    inp+=["-i",mp3]; fc+=f"[{j+1}:a]adelay={int(st*1000)}:all=1[a{j}];"; mr+=f"[a{j}]"
fc+=f"{mr}amix=inputs={len(auds)}:duration=longest:normalize=0[m];[m]loudnorm=I=-17:TP=-2:LRA=11,aresample=48000[ao]"
flat=f"{TMP}/flat.mp4"
subprocess.run(["ffmpeg","-v","error"]+inp+["-filter_complex",fc,"-map","0:v","-map","[ao]","-c:v","libx264","-crf","16",
    "-preset","medium","-pix_fmt","yuv420p","-r","25","-c:a","aac","-b:a","192k","-ar","48000","-ac","2","-shortest","-y",flat],check=True)

nf=int(subprocess.check_output(["ffprobe","-v","error","-select_streams","v:0","-count_frames","-show_entries","stream=nb_read_frames","-of","default=noprint_wrappers=1:nokey=1",flat]).decode().strip())
rz=0.035/nf
out=OUTDIR+f"{name}.mp4"
vf=f"scale=2600:1680:flags=lanczos,unsharp=3:3:0.4:3:3:0.0,zoompan=z='min(1.0+{rz}*on,1.035)':d=1:x=0:y=0:s=1950x1260:fps=25,setsar=1"
subprocess.run(["ffmpeg","-v","error","-i",flat,"-vf",vf,"-c:v","libx264","-crf","16","-preset","slow","-pix_fmt","yuv420p","-r","25","-c:a","copy","-y",out],check=True)
print(f"DONE {name}: {cum:.1f}s -> {out}")
