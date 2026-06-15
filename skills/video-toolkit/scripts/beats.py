import subprocess, sys
# beats.py <footage>  -> prints the content-change (motion) timestamps from freezedetect.
# For a tape that clears before each command, events alternate: result1, clear2, result2, clear3, result3, ...
SRC = sys.argv[1]
out = subprocess.run(["ffmpeg","-hide_banner","-nostats","-i",SRC,"-vf","freezedetect=n=-50dB:d=0.8",
    "-map","0:v","-f","null","-"], capture_output=True, text=True).stderr
ev=[]
for line in out.splitlines():
    if "freeze_end" in line:
        try: ev.append(round(float(line.split("freeze_end:")[1].strip().split()[0]),2))
        except: pass
ev=sorted(set(ev))
print("EVENTS:", ev)
