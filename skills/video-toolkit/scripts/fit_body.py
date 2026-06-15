import subprocess, sys, os
# fit_body.py <prefix> : ensure each body clip fits its beat slot (atempo only when it would overrun).
P = sys.argv[1]
SEGS=["r02a","r02b","r03","r04","r05","r06","r07","r09","r10","rb1","rb2","r12","r13a","r13b","r14a","r14b","r15a","r15b","r16a","r16b"]
BST =[50,6800,15500,20400,35500,54500,69900,87000,92700,102500,109400,114600,120100,124600,127100,132400,135400,139700,145300,147700]
BODY_END=149100
base=os.environ.get("WORKDIR", ".").rstrip("/")+"/vo/"
def dur(p): return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",p]).decode().strip())
for i,seg in enumerate(SEGS):
    nxt = BST[i+1] if i+1<len(BST) else BODY_END
    slot = (nxt - BST[i] - 120)/1000.0
    src=f"{base}{P}_{seg}.mp3"; out=f"{base}_fit_{P}_{seg}.mp3"
    d=dur(src)
    if d>slot and slot>0.3:
        tempo=min(d/slot,1.3)
        subprocess.run(["ffmpeg","-v","error","-i",src,"-filter:a",f"atempo={tempo:.4f}","-y",out],check=True)
        print(f"{seg}: {d:.1f}->{slot:.1f} atempo {tempo:.3f}")
    else:
        subprocess.run(["ffmpeg","-v","error","-i",src,"-c","copy","-y",out],check=True)
        print(f"{seg}: {d:.1f} ok ({slot:.1f})")
