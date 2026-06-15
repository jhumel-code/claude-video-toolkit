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
| `voice` | string | narration | English-locked TTS voice |
| `pronounce` | map | narration | respell coined words for TTS (on-screen text stays correct) |

Paths (`logo`, `fonts_dir`) resolve relative to the **toolkit root** (the parent of
`scripts/`). Override the profiles directory with `BRAND_PROFILE_DIR`.

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
```

## How scripts consume it

- **`brand_intro.py`** reads wordmark, palette, pills, tagline, logo, fonts from the
  active profile. Output goes to `OUT_DIR` (env). Nothing brand-specific is hardcoded.
- **`finish.sh`** takes the grade via `$GRADE`; wire a profile's grade in:
  ```bash
  GRADE="$(python scripts/brand_config.py grade trustabl)" \
    bash scripts/finish.sh intro_silent.mp4 intro.mp4 brand
  ```

## Add a new brand (3 steps)

1. `cp profiles/example-northwind.json profiles/acme.json` and edit the values.
2. Put `acme`'s logo in `assets/` and (optional) fonts in `fonts/`; point `logo` /
   `font_family` at them.
3. Render: `BRAND_PROFILE=acme OUT_DIR=./out python scripts/brand_intro.py intro`, then
   `GRADE="$(python scripts/brand_config.py grade acme)" bash scripts/finish.sh out/intro_silent.mp4 out/intro.mp4`.

That's it — same engine, new brand. The `example-northwind` profile is the reference for
what a non-Trustabl brand looks like end to end.
