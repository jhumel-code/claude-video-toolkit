"""narrate.py - the shared engine behind the narrated-video builders (vid.py, session_vid.py).

The house rules live here once, so the builders cannot drift apart again:
  - the voice comes from the spec's `tts` block, else the brand profile's `tts` block,
    else edge-tts with the spec/profile `voice` and `rate` (tts_engines.py voices it:
    edge, kokoro or chatterbox). *MultilingualNeural voices are refused: they
    code-switch on coined words.
  - narration is respelled through the pronounce map (shared jargon + brand) before TTS,
    and voiced sentences are cached by voice settings + spoken text, so re-runs are fast
    and can never reuse a stale clip after the text changes.
  - every clip is encoded ONCE, straight onto the output canvas. Footage that already
    matches the canvas is untouched (terminal pixels stay crisp), larger footage is
    scaled down to fit, smaller footage is padded ("fit": "scale" upscales it instead).
    Aspect ratio is always kept; nothing is ever stretched.
  - narration is placed at the MEASURED clip boundaries, so audio cannot drift.
  - the <name>.beats.json sidecar that review.sh keys off is always written.
"""
import hashlib, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from brand_config import load_profile            # noqa: E402
from pronounce import jargon_in, load_map   # noqa: E402
from tts_engines import speak                # noqa: E402
from narration_lint import lint             # noqa: E402

FPS = 25
DEFAULT_VOICE = "en-US-AvaNeural"
DEFAULT_RATE = "+0%"
DEFAULT_CANVAS = (2560, 1440)
DEFAULT_PAD = "#070E1A"
ENC = ["-c:v", "libx264", "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p"]


def run(cmd):
    subprocess.run(cmd, check=True)


def dur(path):
    return float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path]).decode().strip())


class Build:
    def __init__(self, spec):
        self.spec = spec
        self.name = spec["name"]
        self.work = os.environ.get("WORKDIR", ".")
        self.outdir = os.path.join(self.work, spec.get("outdir", ""))
        self.tmp = os.path.join(self.work, f"_v_{self.name}")
        self.tts_dir = os.path.join(self.work, "_tts")
        for d in (self.outdir or ".", self.tmp, self.tts_dir):
            os.makedirs(d, exist_ok=True)

        prof = load_profile(spec.get("brand"))
        term = prof.get("terminal", {})
        self.voice = spec.get("voice") or prof.get("voice") or DEFAULT_VOICE
        if "multilingual" in self.voice.lower():
            sys.exit(f"refusing voice {self.voice}: multilingual voices code-switch on coined "
                     f"words. Use an English-locked voice such as {DEFAULT_VOICE}.")
        self.rate = spec.get("rate") or prof.get("rate") or DEFAULT_RATE
        self.tts_cfg = dict(spec.get("tts") or prof.get("tts")
                            or {"engine": "edge", "voice": self.voice, "rate": self.rate})
        self.pmap = load_map(brand=spec.get("brand"))
        if spec.get("canvas"):
            self.canvas = tuple(int(v) for v in spec["canvas"].lower().split("x"))
        elif term.get("width") and term.get("height"):
            self.canvas = (int(term["width"]), int(term["height"]))
        else:
            self.canvas = DEFAULT_CANVAS
        self.pad = (spec.get("pad_color") or term.get("margin_fill") or DEFAULT_PAD).replace("#", "0x")
        self.fit = spec.get("fit", "pad")
        self.gap = float(spec.get("gap", 0.4))
        self._probe = {}
        self.clips, self.auds, self.meta, self.cum = [], [], [], 0.0

    def lint(self, texts):
        """Warn about AI-sounding lines; stop on errors (em dashes, structural labels)."""
        errors = 0
        for key, text in texts:
            for level, msg in lint(text):
                print(f"{key}: {level}: {msg}")
                errors += level == "error"
        if errors:
            sys.exit(f"{errors} narration lint error(s): fix the script before voicing it")

    # ---- inputs -------------------------------------------------------------------------
    def footage(self, override=None):
        return os.path.join(self.work, override or self.spec["footage"])

    def probe(self, path):
        if path not in self._probe:
            if not os.path.exists(path):
                sys.exit(f"footage not found: {path}")
            wh = subprocess.check_output(
                ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                 "stream=width,height", "-of", "csv=p=0", path]).decode().strip().split(",")
            self._probe[path] = (int(wh[0]), int(wh[1]), dur(path))
        return self._probe[path]

    def tts(self, text):
        key = hashlib.sha1((json.dumps(self.tts_cfg, sort_keys=True) + text).encode("utf-8")).hexdigest()[:16]
        wav = os.path.join(self.tts_dir, f"line_{key}.wav")
        if not os.path.exists(wav):
            speak(text, wav + ".part.wav", self.tts_cfg, self.pmap, self.tts_dir)
            os.replace(wav + ".part.wav", wav)
        return wav

    # ---- video --------------------------------------------------------------------------
    def fit_vf(self, w, h):
        cw, ch = self.canvas
        if (w, h) == (cw, ch):
            return "setsar=1"
        s = min(cw / w, ch / h)
        pre = ""
        if s < 1 or self.fit == "scale":
            pre = f"scale={int(w * s) // 2 * 2}:{int(h * s) // 2 * 2}:flags=lanczos,"
        return f"{pre}pad={cw}:{ch}:(ow-iw)/2:(oh-ih)/2:color={self.pad},setsar=1"

    def _encode(self, in_args, vf, out, total):
        run(["ffmpeg", "-nostdin", "-v", "error", *in_args, "-an", "-vf", vf, "-r", str(FPS), *ENC, "-y", out])
        got = dur(out)
        if got < total - 1.5 / FPS:
            sys.exit(f"{out}: clip is {got:.2f}s but its narration needs {total:.2f}s")
        return out

    def clip(self, src, start, play, total, tag):
        """Footage [start, start+play), then the last frame held until `total` seconds."""
        w, h, flen = self.probe(src)
        avail = flen - start
        if avail < 1.0 / FPS:
            sys.exit(f"{tag}: start {start:.2f}s is past the end of {src} ({flen:.2f}s)")
        play = max(1.0 / FPS, min(play, avail))
        vf = self.fit_vf(w, h)
        if total - play > 0.02:
            vf += f",tpad=stop_mode=clone:stop_duration={total - play:.3f}"
        return self._encode(["-ss", f"{start:.3f}", "-t", f"{play:.3f}", "-i", src], vf,
                            os.path.join(self.tmp, f"{tag}.mp4"), total)

    def stretch(self, src, t_in, t_out, total, tag):
        """Footage [t_in, t_out) time-stretched to exactly `total` seconds."""
        w, h, _ = self.probe(src)
        vf = f"{self.fit_vf(w, h)},setpts={total / (t_out - t_in):.5f}*PTS,fps={FPS}"
        return self._encode(["-ss", f"{t_in:.3f}", "-to", f"{t_out:.3f}", "-i", src], vf,
                            os.path.join(self.tmp, f"{tag}.mp4"), total)

    # ---- timeline -----------------------------------------------------------------------
    def add(self, bid, kind, text, mp3, clip, **extra):
        at = round(self.cum + 0.1, 3)
        self.clips.append(clip)
        self.auds.append((mp3, at))
        self.cum += dur(clip)
        jar = jargon_in(text, self.pmap)
        beat = {"id": bid, "kind": kind, "narr_start_s": at, "narr_text": text,
                "beat_end_s": round(self.cum, 3), "jargon": jar,
                "spoken": {k: self.pmap[k] for k in jar},
                "expected_onscreen": extra.get("expected") or []}
        if kind == "result":
            beat["scroll_top"] = extra.get("scroll_top") or []
            beat["play_b"] = bool(extra.get("play_b"))
        self.meta.append(beat)

    def finish(self):
        lst = os.path.join(self.tmp, "list.txt")
        with open(lst, "w", encoding="utf-8") as f:
            for c in self.clips:
                f.write("file '" + os.path.abspath(c).replace("\\", "/") + "'\n")
        silent = os.path.join(self.tmp, "silent.mp4")
        run(["ffmpeg", "-nostdin", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", "-y", silent])

        inp, fc, mix = ["-i", silent], "", ""
        for j, (mp3, st) in enumerate(self.auds):
            inp += ["-i", mp3]
            fc += f"[{j + 1}:a]adelay={int(round(st * 1000))}:all=1[a{j}];"
            mix += f"[a{j}]"
        fc += (f"{mix}amix=inputs={len(self.auds)}:duration=longest:normalize=0,"
               f"loudnorm=I=-17:TP=-2:LRA=11,aresample=48000,apad[ao]")
        out = os.path.join(self.outdir, f"{self.name}.mp4")
        # video is stream-copied: the clips above were the only video encode
        run(["ffmpeg", "-nostdin", "-v", "error", *inp, "-filter_complex", fc, "-map", "0:v", "-map", "[ao]",
             "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
             "-shortest", "-y", out])

        side = os.path.join(self.outdir, f"{self.name}.beats.json")
        with open(side, "w", encoding="utf-8") as f:
            json.dump({"name": self.name, "canvas": "x".join(map(str, self.canvas)),
                       "tts": self.tts_cfg, "beats": self.meta},
                      f, ensure_ascii=False, indent=1)
        print(f"DONE {self.name}: {self.cum:.1f}s, {len(self.meta)} narrated clips, "
              f"{self.tts_cfg.get('engine', 'edge')} {self.tts_cfg.get('voice', '')} -> {out}")
        return out
