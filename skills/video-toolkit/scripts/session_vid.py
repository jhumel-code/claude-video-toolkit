import subprocess, os, sys, json
# session_vid.py -> narrated re-pace of a real Claude Code session (full.mp4)
# speed-fit "action" spans, freeze-hold on result frames; Ava (english-locked) VO.
# Emits <out>.beats.json for scripts/review.sh and applies profiles/pronounce.json to narration.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from pronounce import normalize as _pron, jargon_in as _jarg
except Exception:
    _pron = lambda t: t; _jarg = lambda t: []
base = os.environ.get("WORKDIR", ".").rstrip("/") + "/"
SRC  = base + "plugin-demo/full.mp4"
V    = "en-US-AvaNeural"
OUT  = os.environ.get("OUT_DIR", ".").rstrip("/") + "/session-demo.mp4"
TMP  = base + "_pv"; os.makedirs(TMP, exist_ok=True)
GAP  = 0.35

# each scene: text + how to source footage.
#   freeze: hold a single frame at 'at' for the narration length
#   speed : take footage [in,out] and time-stretch it to the narration length
SCENES = [
 {"t":"This is Claude Code, and it just wrote an A-I agent: an on-call assistant, with tools that call out to check service status and open incidents. The code runs. But agent code fails in ways an ordinary linter never sees. So before it's committed, we let Claude Code audit its own work, with the Trustabl plugin.",
  "mode":"speed","in":13,"out":33},
 {"t":"One request kicks off the trustabl-scan skill. It runs a full static analysis right inside the session, with no C-I and no context switch, modeling every tool the agent declares and checking each one against a security and reliability rule catalog.",
  "mode":"speed","in":33,"out":44},
 {"t":"Twelve findings, and a starting score of just zero point seven one. Two are high severity: both network calls have no timeout, so a single hung dependency could stall the entire agent. The rest flag untyped parameters, missing docstrings, no failure handler, and tracing left on by default. Each one ships with the reason it matters and the exact fix.",
  "mode":"freeze","at":47},
 {"t":"Now the other half of the plugin: trustabl-enrich. It takes those findings and applies them straight to the source, adding timeouts, typing the parameters, writing docstrings and a failure handler, and a guidance doc for the project. It doesn't improvise; it follows the scanner's own fix guidance, finding by finding.",
  "mode":"speed","in":55,"out":96},
 {"t":"Then it re-scans, to check its own work, and this is the part that matters. The score jumps to zero point nine seven, but one finding still remains. So it fixes that one too, and scans again. It doesn't stop at good enough.",
  "mode":"speed","in":96,"out":168},
 {"t":"Zero actionable findings. A clean one point zero, up from zero point seven one. Every issue closed before a single line of code was committed.",
  "mode":"freeze","at":205},
 {"t":"That's the Trustabl plugin for Claude Code: your agent code, audited and hardened the moment it's written, by the same assistant that wrote it. Add it from the marketplace, and ship agents you can trust.",
  "mode":"freeze","at":205},
]

def dur(p): return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",p]).decode().strip())
def tts(text,out): subprocess.run(["python","-m","edge_tts","--voice",V,"--text",_pron(text),"--write-media",out],check=True)

clips=[]; auds=[]; cum=0.0; meta=[]
for i,s in enumerate(SCENES):
    mp3=f"{TMP}/{i}.mp3"; tts(s["t"],mp3); ld=dur(mp3)
    seg=round(ld+GAP,3)                       # scene video length == audio slot
    at=round(cum+0.1,3)
    out=f"{TMP}/{i}.mp4"
    if s["mode"]=="freeze":
        png=f"{TMP}/{i}.png"
        subprocess.run(["ffmpeg","-v","error","-ss",str(s["at"]),"-i",SRC,"-frames:v","1","-y",png],check=True)
        subprocess.run(["ffmpeg","-v","error","-loop","1","-i",png,"-t",f"{seg}","-r","25",
            "-c:v","libx264","-crf","18","-preset","medium","-pix_fmt","yuv420p","-y",out],check=True)
    else:
        L=s["out"]-s["in"]; f=round(seg/L,5)   # stretch [in,out] to fill seg
        subprocess.run(["ffmpeg","-v","error","-ss",str(s["in"]),"-to",str(s["out"]),"-i",SRC,
            "-vf",f"setpts={f}*PTS,fps=25","-an","-c:v","libx264","-crf","18","-preset","medium","-pix_fmt","yuv420p","-y",out],check=True)
    clips.append(out); auds.append((mp3,at)); cum+=seg
    meta.append({"id":f"s{i}","kind":"result","narr_start_s":at,"narr_text":s["t"],
                 "beat_end_s":round(cum,3),"jargon":_jarg(s["t"]),"expected_onscreen":s.get("expect",[])})

json.dump({"beats":meta}, open(OUT.replace(".mp4",".beats.json"),"w"), ensure_ascii=False, indent=1)
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
rz=0.03/nf
vf=f"scale=2600:1680:flags=lanczos,unsharp=3:3:0.4:3:3:0.0,zoompan=z='min(1.0+{rz}*on,1.03)':d=1:x=0:y=0:s=1950x1260:fps=25,setsar=1"
subprocess.run(["ffmpeg","-v","error","-i",flat,"-vf",vf,"-c:v","libx264","-crf","16","-preset","slow","-pix_fmt","yuv420p","-r","25","-c:a","copy","-y",OUT],check=True)
print(f"DONE plugin demo: {cum:.1f}s -> {OUT}")
