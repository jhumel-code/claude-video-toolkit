# 04 · Brand Intro & Animated Banner

> **Brand-driven:** wordmark, palette, pills, tagline, logo and fonts come from the
> active brand profile (`profiles/<name>.json`, via `BRAND_PROFILE`); output dir via
> `OUT_DIR`. See [11-brand-profiles](11-brand-profiles.md). Values below describe the
> Trustabl example profile.

> **Only for brands without an official intro.** If the profile sets `intro_clip`
> (Trustabl does: `assets/trustabl-intro.mp4`, rendered from the Remotion template's
> `DemoIntro`), that clip is the intro and `brand_intro.py intro` refuses to run. A
> generated Trustabl intro was rejected twice (2026-08-05, 2026-08-29). Banners are
> still fine to generate.

`brand_intro.py` generates a branded motion-graphics intro (and a 2:1 banner) with
**Pillow + numpy**: no browser, no After Effects. Deterministic frame-by-frame,
2× supersampled for crisp anti-aliasing, additive glow/bloom for the teal look.

## Concept (the approved sequence, ~6.4s)

1. **Field in** — deep navy field; teal chevron motif + glowing particles fade in.
2. **Forge** — light particles **converge to center and bloom into the shield**
   (the real `logo.png`), with a seal flash + teal glow.
3. **Lockup** — shield settles beside the **Trustabl** wordmark (Poppins SemiBold).
4. **Resolve**: thin teal rule, the profile's tagline, and a row of the profile's
   capability `pills`.

> An earlier version opened with an **audit phase** (agent graph + scan beam +
> red/amber→green findings + a readiness score). That was **cut** per feedback and is
> no longer in the code; the shipped intro is the pure-brand forge above.

## Run

```bash
BRAND_PROFILE=<p> OUT_DIR=<dir> python scripts/brand_intro.py intro        # 1950x1260 -> intro_silent.mp4
BRAND_PROFILE=<p> OUT_DIR=<dir> python scripts/brand_intro.py banner       # 1920x960 (2:1) -> banner_silent.mp4
BRAND_PROFILE=<p> OUT_DIR=<dir> python scripts/brand_intro.py intro mock   # 6-frame storyboard (bi_intro_mock.png)
```
A full intro renders ~160 supersampled frames; check the mock first. The intro is
1950x1260: pass it through `assemble.py`, which fits it to the body's canvas.
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
- **`CAPS`**: the capability pill labels, read from the profile's `pills`.

## Brand specifics

- Teal `#51C1B5` = `(81,193,181)`. Logo = `assets/logo.png` (teal) / `logo_white.png`.
- Wordmark = **Poppins SemiBold** (bundled in `fonts/`), white.
- The logo is trimmed to its content bbox automatically and cached per brand as
  `_logo_<profile>.png` in `OUT_DIR`.

See **[brand.md](brand.md)** for the full palette + asset inventory.

## Two framings

The layout is fractional (positions are `w*…`, `h*…`), so the same `frame(t)` adapts
to both `1950×1260` (intro) and `1920×960` (banner). For a banner that matches the
official left-aligned marketing layout (lockup top-left, motif right), re-position
the lockup group — the elements are all there.
