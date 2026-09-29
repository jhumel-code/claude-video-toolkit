#!/usr/bin/env python3
"""narration_lint.py <file>... : flag narration that reads like AI copy, before it is voiced.

Errors (exit 1): em or en dashes, structural labels ("Act one", "Part 2", "Step 3").
Warnings: sentences over 25 words, "X: the Y" reveals, "not X; Y" constructions,
semicolons, list stacking (5+ commas in a sentence), filler words (crucially, seamless,
robust, leverage, delve, plainly, exactly, ...), and 60+ words without a single
contraction. See references/14-narration-voice.md for the rules behind each one.

Files: a v3 narration.json (sections[].text), a vid.py spec (beats[].a/.b), a
session_vid.py spec (scenes[].t), or plain text. Also importable: lint(text).
"""
import json, os, re, sys

FILLER = ["crucially", "seamless", "seamlessly", "robust", "leverage", "leverages", "delve",
          "plainly", "exactly", "in essence", "ultimately", "it's worth noting",
          "it is worth noting", "pivotal", "testament", "underscores", "at its core"]
CONTRACTION = re.compile(r"n't\b|'(re|ve|ll|d|m)\b|\b(it|that|there|here|what|who|let|he|she)'s\b", re.I)
LABEL = re.compile(r"\b(act|part|step|section|chapter)\s+(one|two|three|four|five|six|seven|"
                   r"eight|nine|ten|\d+)\b", re.I)
REVEAL = re.compile(r":\s+the\b(\s+\S+){0,4}[.!?]$", re.I)


def sentences(text):
    return [s for p in re.split(r"\n\s*\n", text.strip())
            for s in re.split(r"(?<=[.!?])\s+", p.strip()) if s]


def lint(text):
    out = []
    if "—" in text or "–" in text:
        out.append(("error", "em dash: use a period or a comma"))
    m = LABEL.search(text)
    if m:
        out.append(("error", f"structural label: '{m.group(0)}'"))
    for s in sentences(text):
        n = len(s.split())
        short = s if len(s) < 60 else s[:57] + "..."
        if n > 25:
            out.append(("warn", f"long sentence: {n} words, '{short}'"))
        if REVEAL.search(s):
            out.append(("warn", f"colon reveal: '{short}'"))
        if re.search(r"\bnot\b[^.;]{0,50};", s, re.I):
            out.append(("warn", f"not X; Y: '{short}'"))
        elif ";" in s:
            out.append(("warn", f"semicolon: '{short}'"))
        if s.count(",") >= 5:
            out.append(("warn", f"list stacking: {s.count(',')} commas, '{short}'"))
    for w in FILLER:
        if re.search(r"\b" + re.escape(w) + r"\b", text, re.I):
            out.append(("warn", f"filler word: '{w}'"))
    if len(text.split()) >= 60 and not CONTRACTION.search(text):
        out.append(("warn", "no contractions: spoken English uses it's, don't, you'll"))
    return out


def items(path):
    if not path.endswith(".json"):
        return [(os.path.basename(path), open(path, encoding="utf-8").read())]
    d = json.load(open(path, encoding="utf-8"))
    if "sections" in d:
        return [(s["id"], s["text"]) for s in d["sections"]]
    if "beats" in d:
        return [(f"b{i}{k}", b[k]) for i, b in enumerate(d["beats"]) for k in ("a", "b") if b.get(k)]
    if "scenes" in d:
        return [(f"s{i}", s["t"]) for i, s in enumerate(d["scenes"])]
    sys.exit(f"{path}: expected sections, beats or scenes")


if __name__ == "__main__":
    errors = 0
    for path in sys.argv[1:]:
        for key, text in items(path):
            for level, msg in lint(text):
                errors += level == "error"
                print(f"{key}: {level}: {msg}")
    sys.exit(1 if errors else 0)
