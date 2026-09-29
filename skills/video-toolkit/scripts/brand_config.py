"""brand_config.py - load a brand profile for the Claude Video Toolkit.

A profile is profiles/<name>.json. Pick one via the BRAND_PROFILE env var
(default "trustabl"). Brand-specific values (wordmark, palette, pills, tagline,
logo, fonts, grade, voice, rate, pronounce, intro_clip, terminal) live in the
profile; the scripts are brand-agnostic.

CLI:
  python brand_config.py show  [name]   # summary
  python brand_config.py grade [name]   # prints the ffmpeg grade filter string
  python brand_config.py intro [name]   # prints the official intro clip path; exit 1 if none
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # toolkit root
PROFILES = os.environ.get("BRAND_PROFILE_DIR", os.path.join(ROOT, "profiles"))

def load_profile(name=None):
    name = name or os.environ.get("BRAND_PROFILE", "trustabl")
    path = os.path.join(PROFILES, f"{name}.json")
    with open(path, encoding="utf-8") as f:
        p = json.load(f)
    p["_name"] = name
    p["_root"] = ROOT
    def _abs(key):
        v = p[key]
        return v if os.path.isabs(v) else os.path.join(ROOT, v)
    p["abs"] = _abs
    return p

def grade_str(p):
    g = p.get("grade", {})
    parts = []
    if "curves_r" in g:
        parts.append(f"curves=r='{g['curves_r']}':g='{g['curves_g']}':b='{g['curves_b']}'")
    if g.get("eq"):          parts.append(f"eq={g['eq']}")
    if g.get("colorbalance"): parts.append(f"colorbalance={g['colorbalance']}")
    return ",".join(parts)

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "show"
    name = sys.argv[2] if len(sys.argv) > 2 else None
    p = load_profile(name)
    if cmd == "grade":
        print(grade_str(p))
    elif cmd == "intro":
        if not p.get("intro_clip"):
            sys.exit(1)
        print(p["abs"]("intro_clip"))
    else:
        t = p.get("terminal", {})
        print(f"profile={p['_name']}  wordmark={p['wordmark']!r}  tagline={p['tagline']!r}")
        print(f"pills={p['pills']}")
        print(f"accent={p['palette']['accent']}  bg_deep={p['palette']['bg_deep']}")
        print(f"logo={p['abs']('logo')}")
        print(f"voice={p.get('voice')}  rate={p.get('rate', '+0%')}  pronounce={p.get('pronounce', {})}")
        print(f"intro_clip={p['abs']('intro_clip') if p.get('intro_clip') else '(none: generate with brand_intro.py)'}")
        print(f"terminal={t.get('width')}x{t.get('height')} font {t.get('font_size')}  "
              f"margin_fill={t.get('margin_fill')}")
        print(f"grade={grade_str(p)}")
