import subprocess, os
# sound_gen.py -> intro_audio.wav : cinematic-restrained, synthesized (royalty-free)
# timed to revised brand_intro.py (~6.4s): pad bed; converge riser+swell (0.95-2.15)
# -> confirm chime + sub thump on the seal (2.15); settle shimmer (2.85);
# 5 soft blips as capability pills appear (4.4-4.9); pad tail to 6.4.
T=os.environ.get("WORKDIR", ".").rstrip("/")+"/_snd"; os.makedirs(T,exist_ok=True)
OUT=os.environ.get("WORKDIR", ".").rstrip("/")+"/intro_audio.wav"; SR=48000; DUR=6.4
def ff(a): subprocess.run(["ffmpeg","-nostdin","-v","error","-y"]+a,check=True)
def sine(f,d): return f"sine=frequency={f}:sample_rate={SR}:duration={d}"
def lav(e,d): return f"aevalsrc=exprs='{e}':s={SR}:d={d}"

# pad bed: open chord C3/G3/C4, lowpass, swell, light reverb
ff(["-f","lavfi","-i",sine(130.81,DUR),"-f","lavfi","-i",sine(196.30,DUR),"-f","lavfi","-i",sine(262.0,DUR),
    "-filter_complex","[0][1][2]amix=inputs=3:normalize=0,lowpass=f=1300,volume=0.13,"
    "afade=t=in:st=0:d=1.6,afade=t=out:st=5.5:d=0.9,aecho=0.8:0.85:55|110:0.3|0.2",f"{T}/pad.wav"])
# converge riser: chirp 200->760 over 1.2s
ff(["-f","lavfi","-i",lav("sin(2*PI*(200*t+233.3*t*t))",1.2),
    "-af","highpass=f=160,afade=t=in:st=0:d=0.25,afade=t=out:st=0.85:d=0.35,volume=0.17",f"{T}/riser.wav"])
# converge swell into seal
ff(["-f","lavfi","-i","anoisesrc=color=brown:duration=0.85:amplitude=0.7:sample_rate=48000",
    "-af","bandpass=f=520:width_type=h:w=900,afade=t=in:st=0:d=0.7,afade=t=out:st=0.72:d=0.13,volume=0.22",f"{T}/conv.wav"])
# confirm chime: bell G5/D6/G6 exp decay + reverb
ff(["-f","lavfi","-i",sine(784,1.6),"-f","lavfi","-i",sine(1175,1.6),"-f","lavfi","-i",sine(1568,1.6),
    "-filter_complex","[0][1][2]amix=inputs=3:normalize=0,volume='exp(-3.4*t)':eval=frame,"
    "aecho=0.85:0.9:90|180:0.3|0.18,volume=0.3",f"{T}/chime.wav"])
# sub-bass thump
ff(["-f","lavfi","-i",sine(55,0.5),"-af","volume='exp(-8*t)':eval=frame,lowpass=f=160,volume=0.5",f"{T}/thump.wav"])
# settle shimmer
ff(["-f","lavfi","-i","anoisesrc=color=white:duration=1.6:amplitude=0.4:sample_rate=48000",
    "-af","highpass=f=4200,afade=t=in:st=0:d=0.7,afade=t=out:st=1.1:d=0.5,volume=0.05",f"{T}/shim.wav"])
# capability blips (rising)
for i,f in enumerate([1200,1280,1360,1450,1550]):
    ff(["-f","lavfi","-i",sine(f,0.09),"-af","volume='exp(-26*t)':eval=frame,volume=0.16",f"{T}/cap{i}.wav"])

items=[("pad.wav",0),("riser.wav",950),("conv.wav",1350),("chime.wav",2150),("thump.wav",2150),("shim.wav",2850),
       ("cap0.wav",4400),("cap1.wav",4520),("cap2.wav",4640),("cap3.wav",4760),("cap4.wav",4880)]
inp=[]; fc=""; mr=""
for j,(f,ms) in enumerate(items):
    inp+=["-i",f"{T}/{f}"]; fc+=f"[{j}:a]adelay={ms}:all=1[a{j}];"; mr+=f"[a{j}]"
fc+=f"{mr}amix=inputs={len(items)}:duration=longest:normalize=0,aresample={SR},loudnorm=I=-15:TP=-1.5:LRA=11[m]"
ff(inp+["-filter_complex",fc,"-map","[m]","-t",str(DUR),"-ac","2","-ar",str(SR),OUT])
print("DONE ->",OUT)
