# Brand Profiles

The Claude Video Toolkit is brand-agnostic. Every brand-specific value lives in a
profile at `profiles/<name>.json`, loaded by `scripts/brand_config.py` and selected
with the `BRAND_PROFILE` env var (default `trustabl`). This page documents the
**Trustabl example profile** as a worked reference. For the full schema and how to add
your own brand, see [`11-brand-profiles.md`](11-brand-profiles.md).

## A profile at a glance

```jsonc
{
  "name": "Trustabl",
  "wordmark": "Trustabl",
  "tagline": "Static analysis for AI agents",
  "pills": ["Scan","Detect","Score","Fix hints","JSON/SARIF"],
  "logo": "assets/logo.png",          // relative to toolkit root; trimmed at render
  "fonts_dir": "fonts", "font_family": "Poppins",
  "palette": { "accent":[81,193,181], "accent_hi":[150,235,220],
               "bg_deep":[0,9,15], "bg_lift":[2,33,40],
               "text":[247,249,247], "subtext":[150,166,178] },
  "grade": { ... },                    // finish.sh color grade (see docs/11)
  "voice": "en-US-AvaNeural",
  "pronounce": { "Trustabl": "Trustable" }
}
```

## The Trustabl example brand

**Logo** — a teal shield from a stylized "T" + two downward chevron-checkmarks
(*Trust + verified-check + shield*), line-art, rounded caps. Assets in `assets/`:

| File | What | Notes |
|------|------|-------|
| `logo.png` | teal shield, RGBA | primary; teal `#51C1B5` |
| `logo_white.png` | white shield | dark/photo backgrounds |
| `marketing_banner.png` | 2:1 | navy + teal motif + lockup + tagline |
| `github_banner.jpg` | wide | README banner |

`brand_intro.py` trims the logo to its content bbox automatically (cached as
`_logo_brand.png` in `OUT_DIR`).

**Palette**

| Token (profile key) | RGB | Hex |
|-------|-----|-----|
| accent | `(81,193,181)` | `#51C1B5` |
| accent_hi | `(150,235,220)` | `#96EBDC` |
| bg_deep | `(0,9,15)` | `#00090F` |
| bg_lift | `(1,36,43)` | `#01242B` |
| text | `(247,249,247)` | `#F7F9F7` |
| subtext | `(150,166,178)` | `#96A6B2` |

**Typography** — wordmark "Trustabl" in **Poppins** SemiBold (bundled, OFL). Swap
`font_family` + drop the TTFs in `fonts/` to change it.

**Copy** — tagline "Static analysis for AI agents"; pills (accurate-capability set)
`Scan · Detect · Score · Fix hints · JSON/SARIF`.

**Naming** — product = **Trustabl** (capital T) in prose; lowercase `trustabl` only for
machine identifiers. Never an em dash in copy.

> To make a different brand, copy `profiles/example-northwind.json`, change the values,
> point `logo`/`fonts_dir` at your assets, and render with `BRAND_PROFILE=yourbrand`.
