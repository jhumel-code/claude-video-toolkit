#!/usr/bin/env python3
"""beats.py <footage.mp4> [--spec spec.json] [--sheet sheet.png] [--fps 12.5]

Pins the beats of a clear-before-each-command terminal recording (the gentape.py / house
tape structure) and prints ts / res per beat, ready for a vid.py spec.

It measures the footage's "ink" (bright text pixels at 640x360) and reads the tape's shape:
a `clear` drops the ink to the floor, typing raises it a character at a time, the pause
before Enter holds it flat, and output raises it in jumps. The cursor blink (about 32 px of
ink) is flattened with a short trailing max so it cannot fake an event. Per beat:
  ts         typing starts
  first_out  output starts appearing
  res        output ~complete: first sample at 97% of the beat's plateau (streaming output
             keeps growing after its first line). For scroll / stream beats that should play
             through the narration ("play_b"), use first_out as res instead.
  end        the last frame of the hold, before the next `clear` is typed. Keep it in the
             spec: vid.py never plays past it, so a short hold cannot freeze on the
             next command being typed.
A warning is printed when a beat's result is on screen for less than 1.5 s before its clear
(consider a longer hold in the tape). --spec writes a vid.py skeleton with ts/res/end;
--sheet writes one tile per beat at the frame vid.py will hold in phase B. Look at it
before building.
Recordings that do not clear between commands (tmux dual screens, one long stream) need a
contact sheet and hand pins instead.
"""
import argparse, json, os, subprocess, sys
import numpy as np

W, H = 640, 360
BRIGHT = 110      # gray level counted as text ink
MARGIN = 4        # px of ink that counts as a real change once the blink is flattened
HOLD_B = 1.5      # vid.py phase B plays this long before holding the frame


def ink_series(src, fps):
    p = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-i", src, "-vf",
                          f"fps={fps},scale={W}:{H},format=gray", "-f", "rawvideo", "-"],
                         stdout=subprocess.PIPE)
    ink = []
    while True:
        b = p.stdout.read(W * H)
        if len(b) < W * H:
            break
        ink.append(int((np.frombuffer(b, np.uint8) > BRIGHT).sum()))
    p.wait()
    if not ink:
        sys.exit(f"no frames decoded from {src}")
    return np.array(ink, dtype=np.int64)


def trailing_max(x, w):
    return np.array([x[max(0, i - w + 1):i + 1].max() for i in range(len(x))])


def pin(ink, fps):
    w = max(3, round(0.56 * fps))                  # longer than one cursor-off phase
    env_all = trailing_max(ink, w)
    floor = env_all[w:].min() if len(env_all) > w else env_all.min()
    low = floor + MARGIN                           # the empty prompt, cursor on or off
    diffs = np.abs(np.diff(ink))
    toggles = diffs[(diffs >= 8) & (diffs <= 200)]
    blink = int(np.bincount(toggles).argmax()) if len(toggles) else 32
    # a clear is a one-frame drop onto the empty prompt, far bigger than a cursor blink. Found
    # on the raw ink, so a clear stays visible however soon the next command starts typing.
    clears = [i for i in range(1, len(ink)) if ink[i] <= low and ink[i - 1] - ink[i] > max(2 * blink, 24)]
    flat_n = max(3, round(0.4 * fps))              # the pause between typing and Enter
    beats = []
    for s0, s1 in zip([0] + clears, clears + [len(ink)]):
        env = trailing_max(ink[s0:s1], w)          # blink flattened within this beat only
        busy = np.nonzero(env > low)[0]
        if not len(busy):
            continue
        a = s0 + busy[0]
        live = np.nonzero(ink[s0:s1] > low)[0]
        end = s0 + (live[-1] if len(live) else busy[-1])
        if (end - a) / fps < 0.5:
            continue
        seg = env[a - s0:end - s0 + 1]
        d = np.diff(seg, prepend=seg[0])
        # typing ends at the first flat stretch (the pause before Enter)
        typed = next((k for k in range(1, len(seg) - flat_n + 1)
                      if not d[k:k + flat_n].any()), None)
        # drop the trailing `clear` being typed: rises no bigger than a typing step, right
        # before the clear (a flat hold always separates them from the output)
        step = max(16, int(d[1:typed].max()) if typed and typed > 1 else 40) + MARGIN
        tail = len(seg) - 1
        while tail > 0 and 0 < d[tail] <= step:
            tail -= 1
        if typed is not None:
            first = next((k for k in range(typed, tail + 1) if seg[k] > seg[typed] + MARGIN), None)
        else:   # no pause before Enter: take the biggest single rise as the output
            first = int(np.argmax(d[1:tail + 1])) + 1 if tail >= 1 else None
        # end = the last frame of the hold, before the next `clear` starts being typed
        beat = {"k": len(beats), "ts": round(a / fps, 2), "end": round((a + tail) / fps, 2)}
        if first is None:
            res = typed if typed is not None else 0
            beat.update(first_out=None, res=round((a + res) / fps, 2), plateau=int(seg[res]),
                        note="no output found after the command; res = typing end")
        else:
            plateau = seg[first:tail + 1].max()
            res = next(k for k in range(first, tail + 1) if seg[k] >= 0.97 * plateau)
            beat.update(first_out=round((a + first) / fps, 2), res=round((a + res) / fps, 2),
                        plateau=int(plateau))
        if beat["res"] + HOLD_B > beat["end"]:
            beat["warn"] = (f"short hold: the result is on screen {beat['end'] - beat['res']:.2f}s "
                            f"before the clear; vid.py will hold the frame at end={beat['end']}")
        beats.append(beat)
    return beats


def sheet(src, beats, path, flen):
    from PIL import Image, ImageDraw
    tiles = []
    for b in beats:
        t = min(b["res"] + HOLD_B, b["end"], flen - 0.05)   # the frame vid.py will hold
        raw = subprocess.check_output(["ffmpeg", "-nostdin", "-v", "error", "-ss", f"{t:.3f}", "-i", src,
                                       "-frames:v", "1", "-vf", "scale=800:450", "-f", "rawvideo",
                                       "-pix_fmt", "rgb24", "-"])
        im = Image.frombytes("RGB", (800, 450), raw)
        ImageDraw.Draw(im).rectangle([0, 416, 800, 450], fill=(0, 0, 0))
        ImageDraw.Draw(im).text((10, 424), f"beat {b['k']}  ts {b['ts']}  res {b['res']}  "
                                             f"held frame {t:.2f}s", fill=(255, 255, 0))
        tiles.append(im)
    cols = 2 if len(tiles) > 1 else 1
    rows = (len(tiles) + cols - 1) // cols
    out = Image.new("RGB", (800 * cols, 450 * rows))
    for i, im in enumerate(tiles):
        out.paste(im, ((i % cols) * 800, (i // cols) * 450))
    out.save(path)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("footage")
    ap.add_argument("--fps", type=float, default=12.5)
    ap.add_argument("--spec", help="write a vid.py spec skeleton with these pins")
    ap.add_argument("--sheet", help="write a contact sheet of the frames vid.py will hold")
    ap.add_argument("--json", action="store_true", help="print the pins as JSON")
    args = ap.parse_args()

    ink = ink_series(args.footage, args.fps)
    beats = pin(ink, args.fps)
    if args.json:
        print(json.dumps(beats, indent=1))
    else:
        for b in beats:
            print(f"beat {b['k']:2d}  ts {b['ts']:7.2f}  first_out {str(b['first_out']):>7}  "
                  f"res {b['res']:7.2f}  end {b['end']:7.2f}  {b.get('note', '')}")
    for b in beats:
        if "warn" in b:
            print(f"WARN beat {b['k']}: {b['warn']}", file=sys.stderr)
    if args.spec:
        name = os.path.splitext(os.path.basename(args.footage))[0]
        spec = {"name": name, "footage": args.footage,
                "beats": [{"ts": b["ts"], "res": b["res"], "end": b["end"], "a": "", "b": "",
                           "expect": []} for b in beats]}
        with open(args.spec, "w", encoding="utf-8") as f:
            json.dump(spec, f, indent=1)
        print(f"wrote {args.spec}: fill in a/b narration and expect tokens")
    if args.sheet:
        sheet(args.footage, beats, args.sheet, len(ink) / args.fps)
        print(f"wrote {args.sheet}")
