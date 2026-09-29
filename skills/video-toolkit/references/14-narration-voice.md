# 14 · Narration that sounds like a person

A voiceover sounds robotic for two reasons, and they stack: the script reads like AI
copy, and the voice delivers it evenly. Fix the writing first (it's free and certain),
then pick the voice by ear.

## Write for the ear

- Mostly short sentences (under ~16 words, never over 25), one idea each.
- Contractions: it's, don't, you'll, that's. Spoken English uses them.
- Talk to the viewer: "your agent", "you get".
- Plain words. Say an acronym once; never define one mid-sentence.
- At most one list per section, and keep it short.
- Name each thing just before it appears on screen (narrate before show).
- Avoid the AI tells: "X: the Y" reveal openers, "not X; Y" contrasts, tagline fragments
  as closers, filler words (crucially, seamless, robust, leverage, exactly, plainly),
  semicolons, em dashes, structural labels ("Act one", "Part 2").
- Keep every claim to what the footage or diagram shows.

Before (the v2 scan section):
> First, the scan itself. It reads your agent's code and inventories every tool, agent,
> subagent, skill, and MCP server, then checks them against its rules. Most agent failures
> are not exotic exploits; they are misconfigurations right in the definition: an
> over-broad tool, a missing guardrail, a tool that shells out.

After (v3):
> We'll start with the scan. It reads your agent's code and finds everything the agent can
> reach: its tools, its subagents, its skills, and the MCP servers it talks to. Then it
> checks each one against a set of rules.
>
> The problems it finds are usually simple setup mistakes, like a tool that can run any
> shell command, or a guardrail nobody added.

`scripts/narration_lint.py <narration.json | spec.json | file>` flags these patterns; the
builders (`vid.py`, `session_vid.py`, `voice.py`) run it before voicing anything, printing
warnings and stopping on errors. The shipped v2 script drew 33 warnings; v3's draws none.

## Voices

Every builder voices text sentence by sentence through `scripts/tts_engines.py`, joins
the sentences with natural pauses (0.3 s inside a paragraph, 0.65 s between paragraphs),
and caches each sentence, so editing one line re-voices only that line.

| Engine | Voice used | Notes |
|---|---|---|
| `kokoro` (Trustabl's pick, 2026-09-29) | `af_heart`, speed 0.93 | Kokoro-82M, Apache 2.0, local on CPU, fast (a 6-minute explainer in 2 min), deterministic |
| `chatterbox` | default voice | Resemble AI, MIT, local on the GPU, the most expressive, seeded for repeatability. Its default voice runs fast (about 220 words/min): use `exaggeration` 0.3, `cfg_weight` 0.2 and `slow` 0.9. Output carries an inaudible Perth watermark |
| `edge` | `en-US-AvaNeural`, rate -7% | edge-tts, needs the network, flattest delivery; the default when nothing else is set |

Set the voice as a `tts` block: in a vid.py/session_vid.py spec, in a template's
`narration.json`, or in the brand profile (the fallback for both; Trustabl's profile sets
the block below):
```json
"tts": {"engine": "kokoro", "voice": "af_heart", "speed": 0.93}
```
`*MultilingualNeural` voices are refused everywhere (they code-switch on coined words).
The pronounce map applies to every engine.

### Engine setup (one time, Windows; engines live under `~/.claude-video-toolkit/`)
```bash
B=~/.claude-video-toolkit && mkdir -p $B/models/kokoro && cd $B
python -m venv tts-kokoro && tts-kokoro/Scripts/python -m pip install kokoro-onnx soundfile
curl -L -o models/kokoro/kokoro-v1.0.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
curl -L -o models/kokoro/voices-v1.0.bin https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
python -m venv tts-chatterbox
tts-chatterbox/Scripts/python -m pip install torch==2.6.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu124
tts-chatterbox/Scripts/python -m pip install chatterbox-tts   # weights (~3 GB) download on first use
```
Downloads: Kokoro ~355 MB; Chatterbox ~2.5 GB of PyTorch plus ~3 GB of weights. Override
the location with `CVT_TTS_HOME`.

## Choosing a voice (the audition recipe)

You cannot hear audio, so the user picks. Voice the same passage (the real script, not a
test sentence) through each candidate, match the pace (~160 words/min; slow a fast voice
with `slow` or pick a lower speed) and the loudness (-17 LUFS), and stitch the samples into
one file with a spoken label ("Sample one.") in a clearly different voice before each.
Transcribe every sample with whisper first: neural engines can drop or garble words, and
a fast-sounding sample may just be a fast voice. Change one thing at a time: comparing the
old script and the new script in the same voice shows how much the writing alone fixed.
