import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skills", "video-toolkit", "scripts"))
from beats import pin  # noqa: E402

FPS = 12.5


def blink(level, n, start_on=True):
    """A held screen whose cursor blinks: +32 ink for 5 samples, then off for 5."""
    return [level + (32 if ((k // 5) % 2 == 0) == start_on else 0) for k in range(n)]


def test_short_gap_after_clear_still_splits_beats():
    ink = (blink(7, 12)                       # empty prompt before the first command
           + [60, 90, 120, 150] + blink(150, 8)  # type command 1, pause before Enter
           + blink(1400, 14) + [1420]            # output 1 holds, `clear` being typed
           + [39, 39, 7]                         # the clear: only 0.24 s before typing resumes
           + [60, 90, 120] + blink(120, 8)       # type command 2, pause
           + blink(800, 14))                     # output 2 holds to the end
    beats = pin(np.array(ink), FPS)
    assert len(beats) == 2
    assert beats[0]["res"] == round(24 / FPS, 2)   # output 1 appears at sample 24
    assert beats[1]["ts"] == round(42 / FPS, 2)    # typing 2 starts right after the clear


def test_cursor_blink_is_not_a_clear():
    ink = blink(7, 12) + [30, 40] + blink(40, 30)   # a two-letter command whose cursor blinks
    assert len(pin(np.array(ink), FPS)) == 1
