#!/usr/bin/env python3
"""Apply a jargon -> spoken-form map to NARRATION TEXT before edge-tts.

edge-tts has no phoneme / <say-as> / lexicon control (only one prosody tag), so respelling
the text is the only lever to control pronunciation. Apply this ONLY to narration text,
never to recorded footage. When the reviewer flags a new pron_suspect term, add one entry to
profiles/pronounce.json and re-synth just that beat's mp3.

Usage:
  python3 pronounce.py "the DSSE envelope"      # -> "the D S S E envelope"
  echo "..." | python3 pronounce.py
  from pronounce import normalize, jargon_in, load_map
"""
import json, os, re, sys

def load_map(path=None):
    if path is None:
        path = os.environ.get("PRONOUNCE_MAP") or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "profiles", "pronounce.json")
    try:
        return json.load(open(path, encoding="utf-8")).get("map", {})
    except Exception:
        return {}

def _pat(k):
    # word-boundary that also respects hyphen/slash/underscore inside keys
    return r'(?<![\w/-])' + re.escape(k) + r'(?![\w/-])'

def normalize(text, m=None):
    m = load_map() if m is None else m
    for k in sorted(m, key=len, reverse=True):   # longest keys first
        text = re.sub(_pat(k), m[k], text)
    return text

def jargon_in(text, m=None):
    """Return the map keys (original jargon) that appear in text - used to tag beats."""
    m = load_map() if m is None else m
    return [k for k in m if re.search(_pat(k), text)]

if __name__ == "__main__":
    txt = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read()
    sys.stdout.write(normalize(txt))
