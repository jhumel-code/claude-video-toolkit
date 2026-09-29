"""Runs inside the Kokoro venv (tts_engines.py calls it): kokoro_run.py <job.json>
Job: {"model", "voices", "voice", "speed", "items": [{"text", "out"}]}. Loads once."""
import json
import sys

import soundfile as sf
from kokoro_onnx import Kokoro

job = json.load(open(sys.argv[1], encoding="utf-8"))
k = Kokoro(job["model"], job["voices"])
for it in job["items"]:
    samples, sr = k.create(it["text"], voice=job["voice"], speed=float(job["speed"]), lang="en-us")
    sf.write(it["out"], samples, sr)
