import numpy as np, math, random, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from brand_config import load_profile

W,H = (1920,960) if (len(sys.argv)>1 and sys.argv[1]=="banner") else (1950,1260)
MODE = sys.argv[1] if len(sys.argv)>1 else "intro"
SS = 2
w,h = W*SS, H*SS
FPS=25; DUR=6.4; N=int(DUR*FPS)
P = load_profile()                                  # BRAND_PROFILE env (default "trustabl")
OUTDIR = os.environ.get("OUT_DIR", ".")
os.makedirs(OUTDIR, exist_ok=True)
FRM = os.path.join(OUTDIR, f"bi_{MODE}"); os.makedirs(FRM, exist_ok=True)
OUT = os.path.join(OUTDIR, f"{'intro' if MODE=='intro' else 'banner'}_silent.mp4")

def _rgb(k): return tuple(P["palette"][k])
TEAL=_rgb("accent"); TEAL_HI=_rgb("accent_hi"); CYAN=TEAL_HI
WHITE=_rgb("text"); GREY=_rgb("subtext"); DIMTEAL=tuple(int(c*0.62) for c in TEAL)
WMGLOW=tuple(int(c*0.55) for c in TEAL)
BG_DEEP=list(P["palette"]["bg_deep"]); BG_LIFT=list(P["palette"]["bg_lift"])
CAPS=list(P["pills"]); WMTEXT=P["wordmark"]; TAGLINE=P["tagline"]
FONTS_DIR=P["abs"]("fonts_dir"); FONT_FAMILY=P.get("font_family","Poppins")
_logo_trim=os.path.join(OUTDIR,"_logo_brand.png")
if not os.path.exists(_logo_trim):
    _im=Image.open(P["abs"]("logo")).convert("RGBA"); _im.crop(_im.getbbox()).save(_logo_trim)
LOGO=Image.open(_logo_trim).convert("RGBA")
def PF(wgt,size): return ImageFont.truetype(os.path.join(FONTS_DIR,f"{FONT_FAMILY}-{wgt}.ttf"), int(size*SS))

def clamp(x,a=0.,b=1.): return max(a,min(b,x))
def e_out(x): x=clamp(x); return 1-(1-x)**3
def e_in(x): x=clamp(x); return x*x*x
def e_io(x): x=clamp(x); return 4*x*x*x if x<.5 else 1-(-2*x+2)**3/2
def seg(t,a,b): return clamp((t-a)/(b-a))
def lerp(a,b,x): return a+(b-a)*x

yy,xx=np.mgrid[0:h,0:w].astype(np.float32)
cx,cy=w*0.55,h*0.45
rr=np.clip(np.sqrt((xx-cx)**2+((yy-cy)*1.2)**2)/(0.72*math.hypot(w,h)),0,1)
BG=np.zeros((h,w,3),np.float32)
for i,(e,c) in enumerate(zip(BG_DEEP,BG_LIFT)): BG[...,i]=e+(c-e)*(1-rr)**1.7

random.seed(11)
PARTS=[]
for _ in range(80):
    x=w*(0.16+0.84*random.random()**0.5); y=h*random.random()
    s=random.uniform(1.4,3.8); br=random.uniform(0.25,1.0); ph=random.uniform(0,6.28); bok=random.random()<0.13
    PARTS.append((x,y,s*(3.6 if bok else 1),br,ph,bok))
GC=(w*0.5,h*0.42)
random.seed(23)
CONV=[]   # particles that stream into center and forge the shield
for _ in range(26):
    a=random.uniform(0,6.28); rd=random.uniform(0.28,0.5)*h
    CONV.append((GC[0]+math.cos(a)*rd, GC[1]+math.sin(a)*rd, random.uniform(0,0.5), random.uniform(2.0,4.0)))
CAPX,CCY=w*0.70,h*0.44; CHEV=[]
for k in range(11):
    L=(150+k*92)*SS; a=math.radians(30)
    CHEV.append(((CAPX-math.cos(a)*L,CCY-math.sin(a)*L),(CAPX,CCY),(CAPX-math.cos(a)*L,CCY+math.sin(a)*L),k))
def _fieldglow():
    L=Image.new("RGB",(w,h),0); d=ImageDraw.Draw(L)
    for up,ap,dn,k in CHEV:
        c=tuple(int(v*(1-k/13)) for v in TEAL); d.line([up,ap],fill=c,width=int(2*SS)); d.line([ap,dn],fill=c,width=int(2*SS))
    L=L.filter(ImageFilter.GaussianBlur(4*SS))
    P=Image.new("RGB",(w,h),0); d=ImageDraw.Draw(P)
    for x,y,s,br,ph,bok in PARTS: d.ellipse([x-s,y-s,x+s,y+s],fill=tuple(int(v*br) for v in (TEAL_HI if bok else TEAL)))
    return np.asarray(L,np.float32)*0.5+np.asarray(P.filter(ImageFilter.GaussianBlur(6*SS)),np.float32)*0.85
FIELDGLOW=_fieldglow()

def add_glow(base, fn, blur, strength):
    L=Image.new("RGB",(w,h),0); fn(ImageDraw.Draw(L)); base+=np.asarray(L.filter(ImageFilter.GaussianBlur(blur*SS)),np.float32)*strength

def field_crisp(d,t,ramp):
    for up,ap,dn,k in CHEV:
        a=int(60*ramp*(1-k/13))
        if a<2: continue
        d.line([up,ap],fill=TEAL+(a,),width=max(1,int(1.5*SS))); d.line([ap,dn],fill=TEAL+(a,),width=max(1,int(1.5*SS)))
    for x,y,s,br,ph,bok in PARTS:
        tw=0.55+0.45*math.sin(t*1.7+ph); a=int(210*br*tw*ramp)
        d.ellipse([x-s*0.6,y-s*0.6,x+s*0.6,y+s*0.6],fill=(WHITE if bok else TEAL_HI)+(max(0,a),))

_d=ImageDraw.Draw(Image.new("RGB",(8,8)))
WM=WMTEXT; FWM=PF("SemiBold",118); TW=_d.textlength(WM,font=FWM)
LH=210; LW=int(LOGO.width*(LH*SS/LOGO.height)); GAP=int(46*SS)
GW=LW+GAP+TW; GX=w/2-GW/2; LOCK=(GX+LW/2,h*0.40); LOCKH=LH
HERO=(w*0.5,h*0.42); HEROH=360

# timeline
T_CONV=(0.9,2.15); T_SEAL=2.15; T_SHIELD=(2.1,3.0); T_SET=(2.9,3.8)

def shield_img(cxp,cyp,hpx,alpha):
    sc=hpx*SS/LOGO.height; lg=LOGO.resize((max(1,int(LOGO.width*sc)),max(1,int(hpx*SS))),Image.LANCZOS)
    if alpha<1.0: lg.putalpha(lg.split()[3].point(lambda p:int(p*alpha)))
    return int(cxp-lg.width/2),int(cyp-lg.height/2),lg

def frame(t):
    base=BG.copy(); fr=e_out(seg(t,0.0,1.0)); base+=FIELDGLOW*(0.85*fr)
    glob=e_out(seg(t,0.0,0.4))
    # converging particles glow
    cvph=seg(t,*T_CONV)
    if 0<cvph<1:
        def cg(d):
            for sx,sy,dl,sz in CONV:
                p=e_in(clamp((cvph-dl*0.25)/(1-dl*0.25)))
                if p<=0 or p>=1: continue
                x=lerp(sx,GC[0],p); y=lerp(sy,GC[1],p)
                d.ellipse([x-sz*SS,y-sz*SS,x+sz*SS,y+sz*SS],fill=TEAL_HI)
        add_glow(base,cg,7,0.7)
    # seal flash
    fl=seg(t,T_SEAL,T_SEAL+0.55)
    if 0<fl<1:
        r=int((30+fl*560)*SS); add_glow(base,(lambda r:(lambda d:d.ellipse([GC[0]-r,GC[1]-r,GC[0]+r,GC[1]+r],fill=tuple(int(v*0.85) for v in TEAL_HI))))(r),26,0.95*(1-fl))
    sh_a=e_out(seg(t,*T_SHIELD)); st=e_io(seg(t,*T_SET))
    scx=lerp(HERO[0],LOCK[0],st); scy=lerp(HERO[1],LOCK[1],st); shh=lerp(HEROH,LOCKH,st)
    if sh_a>0:
        add_glow(base,(lambda cxp,cyp,hp:(lambda d:d.ellipse([cxp-hp*0.62*SS,cyp-hp*0.62*SS,cxp+hp*0.62*SS,cyp+hp*0.62*SS],fill=tuple(int(v*0.5) for v in TEAL))))(scx,scy,shh),24,0.85*sh_a*(0.7+0.3*math.sin(t*2.2)))
    wm=e_out(seg(t,3.2,4.0))
    if wm>0: add_glow(base,lambda d:d.text((GX+LW+GAP,LOCK[1]),WM,font=FWM,fill=WMGLOW,anchor="lm"),16,0.5*wm)

    img=Image.fromarray(np.clip(base*glob,0,255).astype(np.uint8)).convert("RGBA")
    fg=Image.new("RGBA",(w,h),(0,0,0,0)); d=ImageDraw.Draw(fg)
    field_crisp(d,t,0.9*fr)
    if 0<cvph<1:
        for sx,sy,dl,sz in CONV:
            p=e_in(clamp((cvph-dl*0.25)/(1-dl*0.25)))
            if p<=0 or p>=1: continue
            x=lerp(sx,GC[0],p); y=lerp(sy,GC[1],p); pr=lerp(sx,GC[0],max(0,p-0.06)),lerp(sy,GC[1],max(0,p-0.06))
            a=int(230*(1-p)**0.6)
            d.line([pr[0],pr[1],x,y],fill=TEAL_HI+(int(a*0.6),),width=int(2*SS))
            d.ellipse([x-sz*0.7*SS,y-sz*0.7*SS,x+sz*0.7*SS,y+sz*0.7*SS],fill=WHITE+(a,))
    img.alpha_composite(fg)
    if sh_a>0:
        x,y,lg=shield_img(scx,scy,shh,sh_a); img.alpha_composite(lg,(x,y))
    d=ImageDraw.Draw(img)
    if wm>0: d.text((GX+LW+GAP,LOCK[1]),WM,font=FWM,fill=WHITE+(int(255*wm),),anchor="lm")
    ul=e_out(seg(t,3.7,4.4))
    if ul>0:
        ll=int(300*SS*ul); d.line([w/2-ll,h*0.555,w/2+ll,h*0.555],fill=TEAL+(int(170*ul),),width=int(2*SS))
    tg=e_out(seg(t,3.9,4.6))
    if tg>0: d.text((w/2,h*0.60),TAGLINE,font=PF("Medium",40),fill=GREY+(int(255*tg),),anchor="mm")
    # capability pills (staggered)
    FP=PF("Medium",26); padx=int(22*SS); ph=int(52*SS); g=int(18*SS); cy2=h*0.665
    widths=[d.textlength(c,font=FP)+2*padx for c in CAPS]; total=sum(widths)+g*(len(CAPS)-1); xstart=w/2-total/2
    xx2=xstart
    for i,c in enumerate(CAPS):
        ca=e_out(seg(t,4.4+i*0.12,4.4+i*0.12+0.5))
        bw=widths[i]
        if ca>0.02:
            ry=int((1-ca)*10*SS)
            d.rounded_rectangle([xx2,cy2-ph/2-ry,xx2+bw,cy2+ph/2-ry],radius=int(ph/2),fill=tuple(BG_LIFT)+(int(220*ca),),outline=TEAL+(int(200*ca),),width=max(1,int(1.4*SS)))
            d.text((xx2+bw/2,cy2-ry),c,font=FP,fill=TEAL_HI+(int(255*ca),),anchor="mm")
        xx2+=bw+g
    return img.convert("RGB").resize((W,H),Image.LANCZOS)

if __name__=="__main__":
    if len(sys.argv)>2 and sys.argv[2]=="mock":
        ts=[0.8,1.7,2.3,3.4,4.6,6.0]
        ims=[frame(t).resize((W//3,H//3)) for t in ts]
        sh=Image.new("RGB",(W//3*3,H//3*2))
        for i,im in enumerate(ims): sh.paste(im,((i%3)*(W//3),(i//3)*(H//3)))
        sh.save(BASE+"plugin-demo/bi_mock.png"); print("mock saved t=",ts)
    else:
        for k in range(N):
            frame(k/FPS).save(f"{FRM}/f{k:04d}.png")
            if k%25==0: print("frame",k)
        subprocess.run(["ffmpeg","-v","error","-y","-framerate",str(FPS),"-i",f"{FRM}/f%04d.png","-c:v","libx264","-crf","16","-preset","slow","-pix_fmt","yuv420p","-r",str(FPS),OUT],check=True)
        print("DONE ->",OUT)
