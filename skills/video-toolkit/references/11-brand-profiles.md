# 11 · Brand Profiles

The toolkit is a generic engine; brand identity is data. A profile is
`profiles/<name>.json`, loaded by `scripts/brand_config.py`. Pick one with
`BRAND_PROFILE` (default `trustabl`). Two ship: `trustabl.json` (worked example) and
`example-northwind.json` (a deliberately different brand — warm amber, different
wordmark/pills — that proves the engine is generic).

## Schema

| Field | Type | Used by | Notes |
|-------|------|---------|-------|
| `name` | string | docs/labels | display name |
| `wordmark` | string | `brand_intro.py` | text beside the logo |
| `tagline` | string | `brand_intro.py` | one line under the lockup |
| `pills[]` | string[] | `brand_intro.py` | capability chips; keep ≤5, accurate |
| `logo` | path | `brand_intro.py` | relative to toolkit root; trimmed to bbox at render |
| `fonts_dir` | path | `brand_intro.py` | dir of `<font_family>-<Weight>.ttf` |
| `font_family` | string | `brand_intro.py` | e.g. `Poppins` → `Poppins-SemiBold.ttf` |
| `palette.accent` / `accent_hi` | [r,g,b] | `brand_intro.py` | primary + highlight |
| `palette.bg_deep` / `bg_lift` | [r,g,b] | `brand_intro.py` | background gradient ends |
| `palette.text` / `subtext` | [r,g,b] | `brand_intro.py` | wordmark / tagline |
| `grade.curves_r/g/b` | string | `finish.sh` | ffmpeg `curves` control points |
| `grade.eq` / `colorbalance` | string | `finish.sh` | ffmpeg filter args |
| `tts` | object | `vid.py`, `session_vid.py`, `voice.py` | the narration voice: `{"engine": "kokoro", "voice": "af_heart", "speed": 0.93}` (engines in `14-narration-voice.md`); wins over the profile's `voice`/`rate` |
| `voice` | string | `vid.py`, `session_vid.py` | edge-tts voice when there is no `tts` block (English-locked; multilingual voices are refused) |
| `rate` | string | `vid.py`, `session_vid.py` | edge-tts rate, e.g. `-7%` (default `+0%`) |
| `pronounce` | map | `pronounce.py` → builders | respell coined words for TTS, merged over the shared `profiles/pronounce.json` (on-screen text stays correct) |
| `intro_clip` | path | `assemble.py`, `brand_intro.py` | the brand's official intro. When set, `assemble.py` prepends it by default and `brand_intro.py intro` refuses to generate one |
| `terminal` | object | `gentape.py`, `vid.py`, `assemble.py` | `width`/`height` (= the video canvas), `font_size`, `padding`, `margin`, `margin_fill` (also the pad colour), `border_radius`, `window_bar`, `typing_speed`, optional `font_family`, and a VHS `theme` object |

Paths (`logo`, `fonts_dir`, `intro_clip`) resolve relative to the **toolkit root** (the
parent of `scripts/`). Override the profiles directory with `BRAND_PROFILE_DIR`. A spec's
`tts`, `voice` / `rate` (edge-tts), `canvas` and `pad_color` override the profile for one
video; a spec's
`brand` picks a profile other than `BRAND_PROFILE`.

## Loader (`scripts/brand_config.py`)

```python
from brand_config import load_profile
P = load_profile()              # BRAND_PROFILE env, default "trustabl"
P["wordmark"]; P["palette"]["accent"]; P["abs"]("logo")   # resolved absolute path
```

CLI helpers:

```bash
python scripts/brand_config.py show  trustabl            # summary
python scripts/brand_config.py grade example-northwind   # ffmpeg grade string
python scripts/brand_config.py intro trustabl            # official intro path, exit 1 if none
```

## How scripts consume it

- **`gentape.py`** writes the `terminal` block into every tape; **`vid.py`** /
  **`session_vid.py`** take the canvas and pad colour from it, and the voice (`tts`, else
  `voice`/`rate`) and pronounce map from the profile; **`assemble.py`** prepends `intro_clip`.
- **`brand_intro.py`** reads wordmark, palette, pills, tagline, logo, fonts from the
  active profile. Output goes to `OUT_DIR` (env). Nothing brand-specific is hardcoded.
- **`finish.sh`** takes the grade via `$GRADE`; wire a profile's grade in:
  ```bash
  GRADE="$(python scripts/brand_config.py grade trustabl)" \
    bash scripts/finish.sh intro_silent.mp4 intro.mp4 brand
  ```

## Add a new brand (3 steps)

1. `cp profiles/example-northwind.json profiles/acme.json` and edit the values,
   including the `terminal` theme. If the brand has an official intro video, drop it in
   `assets/` and set `intro_clip`.
2. Put `acme`'s logo in `assets/` and (optional) fonts in `fonts/`; point `logo` /
   `font_family` at them.
3. Render: `BRAND_PROFILE=acme OUT_DIR=./out python scripts/brand_intro.py intro`, then
   `GRADE="$(python scripts/brand_config.py grade acme)" bash scripts/finish.sh out/intro_silent.mp4 out/intro.mp4`.

That's it — same engine, new brand. The `example-northwind` profile is the reference for
what a non-Trustabl brand looks like end to end.
