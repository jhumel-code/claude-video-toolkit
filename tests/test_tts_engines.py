import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skills", "video-toolkit", "scripts"))
from tts_engines import cache_key, layout, split_sentences  # noqa: E402


def test_split_keeps_paragraphs():
    assert split_sentences("A b. C d?\n\nE f!") == [["A b.", "C d?"], ["E f!"]]


def test_split_ignores_single_newlines_inside_a_paragraph():
    assert split_sentences("One two\nthree. Four.") == [["One two three.", "Four."]]


def test_layout_starts_include_pauses():
    starts, total = layout([[1.0, 2.0], [3.0]], sentence=0.3, paragraph=0.65)
    assert starts == [0.0, 1.3, 3.95]
    assert abs(total - 6.95) < 1e-9


def test_cache_key_changes_with_voice_settings():
    a = cache_key({"engine": "kokoro", "voice": "af_heart", "speed": 0.93}, "Hello.")
    b = cache_key({"engine": "kokoro", "voice": "af_heart", "speed": 1.0}, "Hello.")
    c = cache_key({"engine": "kokoro", "voice": "af_heart", "speed": 0.93}, "Hello.")
    assert a != b and a == c
