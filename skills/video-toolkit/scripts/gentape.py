#!/usr/bin/env python3
"""gentape.py <batch.json> -> one VHS .tape per entry, in the brand's house terminal style.

The terminal look (size, font size, margin, theme) comes from the brand profile's
`terminal` block (BRAND_PROFILE, default trustabl), recorded natively at the video canvas
size so vid.py never has to scale it. Structure per tape: a hidden setup line (cd + optional
`setup`), then per beat: type the command, pause, Enter, wait for the prompt, hold; `clear`
between beats. That clear-before-each structure is what scripts/beats.py pins.

Batch entry: {"tape": "f01.tape", "out": "f01-name", "beats": [[command, hold_s], ...],
              "cwd": "/home/demo/demo" (default), "setup": "source ./demo-env.sh" (optional),
              "pause": 2 (seconds between typing and Enter), "wait": 90 (prompt timeout)}
Put env exports in `setup`: the VHS shell does not reliably source ~/.bashrc.
Commands may contain double quotes (they are typed with backticks then); a command with
both a double quote and a backtick has to move into a helper script.
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from brand_config import load_profile

DEFAULT_TERM = {"width": 2560, "height": 1440, "font_size": 28, "padding": 30, "margin": 40,
                "margin_fill": "#070E1A", "border_radius": 12, "window_bar": "Colorful",
                "typing_speed": "35ms"}


def vhs_str(s):
    for q in ('"', "`"):
        if q not in s:
            return f"{q}{s}{q}"
    sys.exit(f"cannot type a command with both \" and ` in one VHS Type; use a helper script: {s}")


def header(out, t):
    h = [f"Output {out}.mp4", 'Set Shell "bash"']
    if t.get("font_family"):
        h.append(f'Set FontFamily "{t["font_family"]}"')
    h += [f"Set FontSize {t['font_size']}", f"Set Width {t['width']}", f"Set Height {t['height']}",
          f"Set Padding {t['padding']}", f"Set Margin {t['margin']}",
          f'Set MarginFill "{t["margin_fill"]}"', f"Set BorderRadius {t['border_radius']}",
          f"Set WindowBar {t['window_bar']}", f"Set TypingSpeed {t['typing_speed']}"]
    if t.get("theme"):
        h.append("Set Theme " + json.dumps(t["theme"]))
    return "\n".join(h) + "\n"


def tape(e, t):
    setup = f"cd {e.get('cwd', '/home/demo/demo')}"
    if e.get("setup"):
        setup += f" && {e['setup']}"
    s = header(e["out"], t)
    s += f"\nHide\nType {vhs_str(setup + ' && clear')}\nEnter\nSleep 2s\nShow\nSleep 1.5s\n\n"
    for i, (cmd, hold) in enumerate(e["beats"]):
        if i > 0:
            s += 'Type "clear"\nEnter\nSleep 0.8s\n'
        s += (f"Type {vhs_str(cmd)}\nSleep {e.get('pause', 2)}s\nEnter\n"
              f"Wait@{e.get('wait', 90)}s /^> ?$/\nSleep {hold}s\n\n")
    return s


if __name__ == "__main__":
    term = {**DEFAULT_TERM, **load_profile().get("terminal", {})}
    workdir = os.environ.get("WORKDIR", ".")
    for e in json.load(open(sys.argv[1], encoding="utf-8")):
        with open(os.path.join(workdir, e["tape"]), "w", encoding="utf-8", newline="\n") as f:
            f.write(tape(e, term))
        print("wrote", e["tape"])
