"""Runs inside the Chatterbox venv (tts_engines.py calls it): chatterbox_run.py <job.json>
Job: {"items": [{"text", "out"}], "exaggeration", "cfg_weight", "seed", "prompt" (optional
reference wav)}. Loads the model once; seeds every sentence so a re-run is repeatable."""
import json
import sys

import torch
import torchaudio as ta
from chatterbox.tts import ChatterboxTTS

job = json.load(open(sys.argv[1], encoding="utf-8"))
model = ChatterboxTTS.from_pretrained(device="cuda" if torch.cuda.is_available() else "cpu")
kw = {"exaggeration": job["exaggeration"], "cfg_weight": job["cfg_weight"]}
if job.get("prompt"):
    kw["audio_prompt_path"] = job["prompt"]
for it in job["items"]:
    torch.manual_seed(job["seed"])
    wav = model.generate(it["text"], **kw)
    ta.save(it["out"], wav, model.sr)
