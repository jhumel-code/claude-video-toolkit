# 04 · Brand Intro & Animated Banner

> **Brand-driven:** wordmark, palette, pills, tagline, logo and fonts come from the
> active brand profile (`profiles/<name>.json`, via `BRAND_PROFILE`); output dir via
> `OUT_DIR`. See [11-brand-profiles](11-brand-profiles.md). Values below describe the
> Trustabl example profile.

`brand_intro.py` generates a branded motion-graphics intro (and a 2:1 banner) with
**Pillow + numpy** — no browser, no After Effects. Deterministic frame-by-frame,
2× supersampled for crisp anti-aliasing, additive glow/bloom for the teal look.

## Concept (the approved sequence, ~6.4s)

1. **Field in** — deep navy field; teal chevron motif + glowing particles fade in.
2. **Forge** — light particles **converge to center and bloom into the shield**
   (the real `logo.png`), with a seal flash + teal glow.
3. **Lockup** — shield settles beside the **Trustabl** wordmark (Poppins SemiBold).
4. **Resolve** — thin teal rule, tagline *"Static analysis for AI agents"*, and a
   row of **capability pills**: `Scan · Auto-fix · Guardrails · SBOM · Vuln-scan`.

> An earlier version opened with an **audit phase** (agent graph + scan beam +
> red/amber→green findings + a readiness score). That was **cut** per feedback — the
> code still shows the technique (graph/beam/finding nodes) if you want it back, but
> the shipped intro is the pure-brand forge above.

## Run

```bash
python vo/brand_intro.py intro            # 1950x1260 video intro  -> intro_silent.mp4
python vo/brand_intro.py banner           # 1920x960 (2:1) banner  -> banner_silent.mp4
python vo/brand_intro.py intro mock       # quick 6-frame storyboard montage (bi_mock.png)
```
Then mux the sound (see [05-sound-design](05-sound-design.md)):
```bash
ffmpeg -i intro_silent.mp4 -i intro_audio.wav -c:v copy -c:a aac -b:a 192k -shortest intro.mp4
```

## How it's built (edit points)

- **`BG`** — numpy radial navy gradient (`#000910` → `#01242b` toward center-right).
- **`FIELDGLOW`** — precomputed once (chevrons + particles blurred) so the per-frame
  render stays fast; per frame just `base += FIELDGLOW*ramp`.
- **`add_glow(base, draw_fn, blur, strength)`** — draw on a black layer, GaussianBlur,
  add to the float base = bloom. Phase-limit glows (only during the phase that needs
  them) to keep it fast.
- **`shield_img(...)`** — composites the real teal logo, scaled, alpha-faded.
- **`frame(t)`** — everything is a function of `t` via easing (`e_out/e_in/e_io`) and
  `seg(t,a,b)` (normalized progress in a window). Timeline constants near the top:
  `T_CONV / T_SEAL / T_SHIELD / T_SET`, plus the wordmark/rule/tagline/pill windows.
- **`CAPS`** — the capability pill labels. Change this list to re-word.

## Brand specifics

- Teal `#51C1B5` = `(81,193,181)`. Logo = `assets/logo.png` (teal) / `logo_white.png`.
- Wordmark = **Poppins SemiBold** (bundled in `fonts/`), white.
- Trim the logo to its content bbox once and save a working copy
  (`_logo_teal.png`); `brand_intro.py` loads that.

See **[brand.md](brand.md)** for the full palette + asset inventory.

## Two framings

The layout is fractional (positions are `w*…`, `h*…`), so the same `frame(t)` adapts
to both `1950×1260` (intro) and `1920×960` (banner). For a banner that matches the
official left-aligned marketing layout (lockup top-left, motif right), re-position
the lockup group — the elements are all there.
