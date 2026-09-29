"""tts_engines.py - voice narration through one of three engines, sentence by sentence.

  edge        edge-tts (Microsoft neural voices, needs network); the default
  kokoro      Kokoro-82M through kokoro-onnx, local, Apache 2.0, runs in its own venv
  chatterbox  Resemble AI Chatterbox, local, MIT, runs in its own venv (CUDA if present);
              its audio carries Resemble's inaudible Perth watermark

speak(text, out_wav, tts, pmap, cache_dir) -> {"dur", "starts", "durs"}
  Splits the text into paragraphs and sentences, respells each sentence with the pronounce
  map, voices every uncached sentence in ONE engine call (so a model loads once), then
  joins them with natural pauses into out_wav (48 kHz stereo). Returns the total length
  and each sentence's start and length, which is what lets reveals follow the narration.

tts settings: {"engine", "voice", "speed" (kokoro), "rate" (edge), "exaggeration" and
"cfg_weight" (chatterbox), "slow" (atempo applied after synthesis, e.g. 0.9), "seed",
"pause": {"sentence": 0.3, "paragraph": 0.65}}. Engines live under CVT_TTS_HOME (default
~/.claude-video-toolkit); references/14-narration-voice.md has the setup commands.
"""
import hashlib, json, os, re, subprocess, sys, tempfile

HOME = os.environ.get("CVT_TTS_HOME") or os.path.join(os.path.expanduser("~"), ".claude-video-toolkit")
RUNNERS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "engines")
DEFAULT_PAUSE = {"sentence": 0.3, "paragraph": 0.65}
SETUP = "see references/14-narration-voice.md (engine setup)"
VOICE_KEYS = ("engine", "voice", "speed", "rate", "exaggeration", "cfg_weight", "slow", "seed")


def split_sentences(text):
    """Paragraphs (blank-line separated) of sentences; single newlines are just spaces."""
    paras = [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n", text.strip())]
    return [[s for s in re.split(r"(?<=[.!?])\s+", p) if s] for p in paras if p]


def layout(durs_by_para, sentence, paragraph):
    """Start time of every sentence once pauses are inserted, and the total length."""
    starts, t = [], 0.0
    for pi, para in enumerate(durs_by_para):
        if pi:
            t += paragraph
        for si, d in enumerate(para):
            if si:
                t += sentence
            starts.append(round(t, 3))
            t += d
    return starts, round(t, 3)


def cache_key(tts, spoken):
    ident = "|".join(str(tts.get(k, "")) for k in VOICE_KEYS) + "|" + spoken
    return hashlib.sha1(ident.encode("utf-8")).hexdigest()[:16]


def _run(cmd):
    subprocess.run(cmd, check=True, stdin=subprocess.DEVNULL)


def _dur(path):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", path], stdin=subprocess.DEVNULL).decode())


def _venv_python(engine):
    for rel in (os.path.join("Scripts", "python.exe"), os.path.join("bin", "python")):
        p = os.path.join(HOME, f"tts-{engine}", rel)
        if os.path.exists(p):
            return p
    sys.exit(f"TTS engine '{engine}' is not set up under {HOME}: {SETUP}")


def _to_cache(raw, out, tts):
    """Engine output -> 48 kHz stereo wav, optionally slowed (pitch kept)."""
    af = ["-af", f"atempo={tts['slow']}"] if tts.get("slow") else []
    _run(["ffmpeg", "-nostdin", "-v", "error", "-i", raw, *af, "-ar", "48000", "-ac", "2", "-y", out])


def _synth(todo, tts, work):
    """Voice [(spoken, cache_wav)] with the configured engine."""
    engine = tts.get("engine", "edge")
    if engine == "edge":
        for i, (spoken, out) in enumerate(todo):
            mp3 = os.path.join(work, f"{i}.mp3")
            _run([sys.executable, "-m", "edge_tts", "--voice", tts.get("voice", "en-US-AvaNeural"),
                  f"--rate={tts.get('rate', '+0%')}", f"--text={spoken}", "--write-media", mp3])
            _to_cache(mp3, out, tts)
        return
    items = [{"text": spoken, "out": os.path.join(work, f"{i}.wav")} for i, (spoken, _) in enumerate(todo)]
    job = {"items": items}
    if engine == "kokoro":
        job.update(model=os.path.join(HOME, "models", "kokoro", "kokoro-v1.0.onnx"),
                   voices=os.path.join(HOME, "models", "kokoro", "voices-v1.0.bin"),
                   voice=tts.get("voice", "af_heart"), speed=float(tts.get("speed", 1.0)))
    elif engine == "chatterbox":
        job.update(exaggeration=float(tts.get("exaggeration", 0.5)),
                   cfg_weight=float(tts.get("cfg_weight", 0.5)), seed=int(tts.get("seed", 0)))
        if tts.get("voice") not in (None, "", "default"):
            job["prompt"] = tts["voice"]
    else:
        sys.exit(f"unknown TTS engine '{engine}': use edge, kokoro or chatterbox")
    jpath = os.path.join(work, "job.json")
    with open(jpath, "w", encoding="utf-8") as f:
        json.dump(job, f)
    quiet = {**os.environ, "TQDM_DISABLE": "1", "HF_HUB_DISABLE_PROGRESS_BARS": "1", "PYTHONWARNINGS": "ignore"}
    subprocess.run([_venv_python(engine), os.path.join(RUNNERS, f"{engine}_run.py"), jpath], check=True,
                   stdin=subprocess.DEVNULL, env=quiet)
    for it, (_, out) in zip(items, todo):
        _to_cache(it["out"], out, tts)


def speak(text, out_wav, tts, pmap, cache_dir):
    from pronounce import normalize
    if "multilingual" in str(tts.get("voice", "")).lower():
        sys.exit(f"refusing voice {tts['voice']}: multilingual voices code-switch on coined words")
    os.makedirs(cache_dir, exist_ok=True)
    paras = split_sentences(text)
    wavs = [[os.path.join(cache_dir, cache_key(tts, normalize(s, pmap)) + ".wav") for s in p] for p in paras]
    todo = [(normalize(s, pmap), w) for p, ws in zip(paras, wavs) for s, w in zip(p, ws)
            if not os.path.exists(w)]
    todo = list(dict.fromkeys(todo))                      # a repeated sentence is voiced once
    if todo:
        with tempfile.TemporaryDirectory() as work:
            _synth(todo, tts, work)
    durs = [[_dur(w) for w in ws] for ws in wavs]
    pause = {**DEFAULT_PAUSE, **tts.get("pause", {})}
    starts, _ = layout(durs, pause["sentence"], pause["paragraph"])

    gap_s, gap_p = (os.path.join(cache_dir, f"_gap_{g:.3f}.wav") for g in (pause["sentence"], pause["paragraph"]))
    for g, path in ((pause["sentence"], gap_s), (pause["paragraph"], gap_p)):
        if not os.path.exists(path):
            _run(["ffmpeg", "-nostdin", "-v", "error", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                  "-t", f"{g:.3f}", "-y", path])
    seq = []
    for pi, ws in enumerate(wavs):
        for si, w in enumerate(ws):
            if si:
                seq.append(gap_s)
            elif pi:
                seq.append(gap_p)
            seq.append(w)
    inp = [a for p in seq for a in ("-i", p)]
    fc = "".join(f"[{i}:a]" for i in range(len(seq))) + f"concat=n={len(seq)}:v=0:a=1[a]"
    _run(["ffmpeg", "-nostdin", "-v", "error", *inp, "-filter_complex", fc, "-map", "[a]", "-y", out_wav])
    return {"dur": round(_dur(out_wav), 3), "starts": starts, "durs": [round(d, 3) for p in durs for d in p]}
