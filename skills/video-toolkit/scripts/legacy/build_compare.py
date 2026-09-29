import subprocess, os
OUT = os.environ.get("OUT_DIR", ".").rstrip("/") + "/voice-test"
GUY = "en-US-GuyNeural"
# (number-label, sample file) in play order
order = [
    ("One.",   "sent_MULTI_Trustabl.mp3"),     # multilingual current (the glitch reference)
    ("Two.",   "sent_MULTI_Trust-able.mp3"),
    ("Three.", "sent_MULTI_Trustabul.mp3"),
    ("Four.",  "sent_MULTI_trust_a_bull.mp3"),
    ("Five.",  "sent_MONO_Trustable.mp3"),       # english-only current
    ("Six.",   "sent_MONO_Trust-able.mp3"),
    ("Seven.", "sent_MONO_Trustabul.mp3"),
    ("Eight.", "sent_MONO_trust_a_bull.mp3"),
]
def tts(text, out, voice=GUY):
    subprocess.run(["python","-m","edge_tts","--voice",voice,"--text",text,"--write-media",out],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
# 0.45s silence spacer
sil = f"{OUT}/_sil.mp3"
subprocess.run(["ffmpeg","-v","error","-f","lavfi","-i","anullsrc=r=24000:cl=mono","-t","0.45","-q:a","9","-y",sil],check=True)

pieces = []
for i,(lab, samp) in enumerate(order):
    lp = f"{OUT}/_lab{i}.mp3"; tts(lab, lp)
    pieces += [lp, sil, f"{OUT}/{samp}", sil, sil]   # label, gap, sample, double-gap

inp = []
for p in pieces: inp += ["-i", p]
fc = "".join(f"[{j}:a]aresample=44100[a{j}];" for j in range(len(pieces)))
fc += "".join(f"[a{j}]" for j in range(len(pieces))) + f"concat=n={len(pieces)}:v=0:a=1[out]"
final = f"{OUT}/COMPARE_listen_to_this.mp3"
subprocess.run(["ffmpeg","-v","error"]+inp+["-filter_complex",fc,"-map","[out]","-q:a","4","-y",final],check=True)
print("built", final)
