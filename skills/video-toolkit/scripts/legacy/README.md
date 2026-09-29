# Legacy scripts (June 2026 Trustabl demo builds)

These built one specific video family: the v17 Trustabl terminal demo and its re-voiced
variants, plus the one-time switch of the marketing batch off the multilingual voice.
They hardcode that demo's narration, beat start times, and file names, so they are
worked examples, not tools. Nothing in the skill calls them.

| Script | What it did |
|--------|-------------|
| `make_voice.sh <voice> <prefix>` | synthesized the v17 narration clip set in one voice |
| `build_voice.sh <prefix>` | rebuilt the v17 demo in that voice on the reference voice's beat starts |
| `build_intro_voice.py <prefix>` | re-paced the v17 intro to the new clip lengths |
| `fit_body.py <prefix>` | atempo-fit any clip that would overrun its slot |
| `build_compare.py` | stitched numbered pronunciation samples into one A/B file |
| `reaudio.py` / `reaudio_batch.sh` | swapped AvaMultilingual narration for AvaNeural on finished videos, picture untouched |

For new work use `scripts/vid.py` / `scripts/session_vid.py` (voice and rate come from the
spec or the brand profile). To re-voice a finished video, re-synthesize each clip and place
it at the `narr_start_s` recorded in the video's `.beats.json` sidecar.
