#!/usr/bin/env bash
# build_voice.sh <prefix>  -> trustabl-demo-<prefix>.mp4 (full v17-style demo in that voice)
set -e
cd "${WORKDIR:-$PWD}"
P="$1"
BODY=trustabl-demo-final.mp4
ENC=(-c:v libx264 -crf 16 -preset medium -pix_fmt yuv420p -r 25 -c:a aac -b:a 192k -ar 48000 -ac 2)
LN="loudnorm=I=-17:TP=-2:LRA=11"
dur(){ ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$1"; }
f(){ python -c "print($1)"; }

# ---------- INTRO ----------
python vo/build_intro_voice.py "$P"
LDA=$(dur vo/${P}_r01a.mp3); LDB=$(dur vo/${P}_r01b.mp3)
SA=100
SB=$(f "int(($LDA+0.4)*1000)+100")
SC=$(f "int(($LDA+0.4+$LDB+0.4)*1000)+100")
ffmpeg -v error -i intro-silent-${P}.mp4 \
  -i vo/${P}_r01a.mp3 -i vo/${P}_r01b.mp3 -i vo/${P}_r01c.mp3 \
  -filter_complex "[1:a]adelay=${SA}:all=1[a1];[2:a]adelay=${SB}:all=1[a2];[3:a]adelay=${SC}:all=1[a3];\
[a1][a2][a3]amix=inputs=3:duration=longest:normalize=0[m];[m]${LN},aresample=48000[ao]" \
  -map 0:v -map "[ao]" "${ENC[@]}" -shortest -y seg_intro_${P}.mp4

# ---------- BODY (silent footage from approved render + re-voiced clips at Ava beat positions) ----------
ffmpeg -v error -ss 18.0 -to 167.1 -i "$BODY" -an "${ENC[@]}" -y _silentbody_${P}.mp4
python vo/fit_body.py "$P"
SEGS=(r02a r02b r03 r04 r05 r06 r07 r09 r10 rb1 rb2 r12 r13a r13b r14a r14b r15a r15b r16a r16b)
BST=(50 6800 15500 20400 35500 54500 69900 87000 92700 102500 109400 114600 120100 124600 127100 132400 135400 139700 145300 147700)
inp=(-i _silentbody_${P}.mp4); fc=""; mr=""
for i in "${!SEGS[@]}"; do idx=$((i+1)); inp+=(-i "vo/_fit_${P}_${SEGS[$i]}.mp3"); fc+="[$idx:a]adelay=${BST[$i]}:all=1[b$idx];"; mr+="[b$idx]"; done
fc+="${mr}amix=inputs=${#SEGS[@]}:duration=longest:normalize=0[m];[m]${LN},aresample=48000[ao]"
ffmpeg -v error "${inp[@]}" -filter_complex "$fc" -map 0:v -map "[ao]" "${ENC[@]}" -shortest -y seg_body_${P}.mp4

# ---------- OUTRO (held proof frame + detailed r17) ----------
ffmpeg -v error -ss 166.0 -i "$BODY" -frames:v 1 -y vo/outro_frame.png
LD17=$(dur vo/${P}_r17.mp3); HOLD=$(f "round($LD17+1.0,2)")
ffmpeg -v error -loop 1 -t ${HOLD} -i vo/outro_frame.png -i vo/${P}_r17.mp3 \
  -filter_complex "[1:a]adelay=500:all=1[a];[a]${LN},aresample=48000[ao]" \
  -map 0:v -map "[ao]" "${ENC[@]}" -shortest -y seg_outro_${P}.mp4

# ---------- FLAT concat ----------
printf "file 'seg_intro_${P}.mp4'\nfile 'seg_body_${P}.mp4'\nfile 'seg_outro_${P}.mp4'\n" > vlist_${P}.txt
ffmpeg -v error -f concat -safe 0 -i vlist_${P}.txt -c copy -y _flat_${P}.mp4

# ---------- QUALITY + LEFT-ANCHORED ZOOM (v17 look) ----------
VENC=(-c:v libx264 -crf 16 -preset slow -pix_fmt yuv420p -r 25)
SS="scale=2600:1680:flags=lanczos,unsharp=3:3:0.4:3:3:0.0"
NI=$(ffprobe -v error -select_streams v:0 -count_frames -show_entries stream=nb_read_frames -of default=noprint_wrappers=1:nokey=1 seg_intro_${P}.mp4)
RI=$(f "0.04/float($NI)")
ffmpeg -v error -i seg_intro_${P}.mp4 -vf "${SS},zoompan=z='min(1.0+${RI}*on,1.04)':d=1:x=0:y=0:s=1950x1260:fps=25,setsar=1" "${VENC[@]}" -c:a copy -y _hi_${P}.mp4
ffmpeg -v error -i seg_body_${P}.mp4 -vf "scale=1950:1260:flags=lanczos,unsharp=3:3:0.4:3:3:0.0,setsar=1" "${VENC[@]}" -c:a copy -y _hb_${P}.mp4
NO=$(ffprobe -v error -select_streams v:0 -count_frames -show_entries stream=nb_read_frames -of default=noprint_wrappers=1:nokey=1 seg_outro_${P}.mp4)
RO=$(f "0.05/float($NO)")
ffmpeg -v error -i seg_outro_${P}.mp4 -vf "${SS},zoompan=z='min(1.0+${RO}*on,1.05)':d=1:x=0:y='ih-ih/zoom':s=1950x1260:fps=25,setsar=1" "${VENC[@]}" -c:a copy -y _ho_${P}.mp4
printf "file '_hi_${P}.mp4'\nfile '_hb_${P}.mp4'\nfile '_ho_${P}.mp4'\n" > hlist_${P}.txt
ffmpeg -v error -f concat -safe 0 -i hlist_${P}.txt -c copy -y trustabl-demo-${P}.mp4

printf "DONE %s: %.2fs  " "$P" "$(dur trustabl-demo-${P}.mp4)"
ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 trustabl-demo-${P}.mp4
