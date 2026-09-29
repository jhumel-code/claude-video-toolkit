# Voice Samples

Every edge-tts voice this toolkit uses, with a comparable sample of each. All
samples speak the **same line** so you can A/B them:

> *"Trustabl runs a full static analysis on your A-I agents. It finds the risks
> and helps you fix them before you ship."*

(The line includes **"Trustabl"** on purpose — play `AvaNeural` vs
`AvaMultilingualNeural` back to back and you'll hear the multilingual voice
mis-pronounce the brand. That glitch is why we switched. See below.)

Generate more samples: `python -m edge_tts --voice <id> --text "..." --write-media out.mp3`

## The voices

| Sample file | Voice id | Role — where & how it's used | Notes |
|-------------|----------|------------------------------|-------|
| **`en-US-AvaNeural.mp3`** | `en-US-AvaNeural` | **PRIMARY narrator.** The Trustabl profile's `voice` (at `rate` -7%), which `vid.py` and `session_vid.py` use. Every current marketing video + the plugin demo uses it. | **English-locked → cannot code-switch.** This is the default for ALL narration. 7.2s. |
| `en-US-AndrewNeural.mp3` | `en-US-AndrewNeural` | **Male narrator variant.** Alternate-voice demo renders (set `voice` in the spec). | Paces ≈ Ava (within ~0.3%) → works with the no-re-pace multi-voice swap. 7.2s. |
| `en-US-EmmaNeural.mp3` | `en-US-EmmaNeural` | **Female narrator variant.** Alternate-voice demo renders. | Paces ≈ Ava (~2% slower). 7.4s. |
| `en-US-GuyNeural.mp3` | `en-US-GuyNeural` | **Utility / label voice.** `scripts/legacy/build_compare.py` used it to speak option numbers ("One.", "Two.") in the A/B pronunciation comparison, so the labels are clearly distinct from the Ava clips being compared. | **Not for narration**: it's ~12% slower (8.1s) and used only as spoken labels. |
| `en-US-AvaMultilingualNeural.mp3` | `en-US-AvaMultilingualNeural` | **DEPRECATED for narration.** The *original* voice; `scripts/legacy/reaudio.py` replaced it with `AvaNeural` across the marketing batch. Kept here only as the "what not to use" reference. The builders refuse it. | Auto-detects language → **code-switches on coined words** ("Trustabl") into another language's phonology. ~8% slower than mono Ava (7.8s). |

## The rule

**Narrate with `en-US-AvaNeural`.** Never the `*MultilingualNeural` variants for
narration — they code-switch, and a spelling change won't fix it (it's the model,
not the text; edge-tts is byte-deterministic so the glitch is reproducible). If you
want a male/female alternate, use `en-US-AndrewNeural` / `en-US-EmmaNeural` (mono),
which pace ≈ Ava so the multi-voice swap pipeline works without a re-pace.

## Pacing (same line, mono Ava = baseline)

```
AvaNeural          7.22s   (baseline — primary)
AndrewNeural       7.20s   (≈ Ava)
EmmaNeural         7.37s   (~2% slower)
AvaMultilingual    7.82s   (~8% slower — and code-switches)
GuyNeural          8.11s   (~12% slower — labels only)
```

A voice within ~1-2% of Ava can be swapped onto Ava's beat starts with no re-pace
(an atempo fit mops up any clip that overruns). A much slower voice (Aria/Jenny are
~15% slower) needs a real re-pace, not a swap. Full detail:
[`../references/06-voice-models.md`](../references/06-voice-models.md).
