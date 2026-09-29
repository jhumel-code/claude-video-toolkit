#!/usr/bin/env python3
"""Apply a jargon -> spoken-form map to NARRATION TEXT before edge-tts.

edge-tts has no phoneme / <say-as> / lexicon control (only one prosody tag), so respelling
the text is the only lever to control pronunciation. Apply this ONLY to narration text,
never to recorded footage. The map is the shared jargon map (profiles/pronounce.json, or
$PRONOUNCE_MAP) plus the brand profile's own `pronounce` respellings (BRAND_PROFILE,
default trustabl), brand entries winning. When the reviewer flags a new pron_suspect term,
add one entry and re-synth just that beat's mp3.

Usage:
  python3 pronounce.py "the DSSE envelope"      # -> "the D S S E envelope"
  echo "..." | python3 pronounce.py
  from pronounce import normalize, jargon_in, load_map
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def load_map(path=None, brand=None):
    if path is None:
        path = os.environ.get("PRONOUNCE_MAP") or os.path.join(HERE, "..", "profiles", "pronounce.json")
    m = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            m.update(json.load(f).get("map", {}))
    sys.path.insert(0, HERE)
    from brand_config import load_profile
    try:
        m.update(load_profile(brand).get("pronounce", {}))
    except FileNotFoundError as e:
        sys.stderr.write(f"[pronounce] no brand profile ({e.filename}); shared map only\n")
    return m


def _pat(k):
    # word-boundary that also respects hyphen/slash/underscore inside keys
    return r'(?<![\w/-])' + re.escape(k) + r'(?![\w/-])'


def normalize(text, m=None):
    m = load_map() if m is None else m
    for k in sorted(m, key=len, reverse=True):   # longest keys first
        text = re.sub(_pat(k), lambda _: m[k], text)
    return text


def jargon_in(text, m=None):
    """Return the map keys (original jargon) that appear in text - used to tag beats."""
    m = load_map() if m is None else m
    return [k for k in m if re.search(_pat(k), text)]


if __name__ == "__main__":
    txt = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read()
    sys.stdout.write(normalize(txt))
