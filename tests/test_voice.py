import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skills", "video-toolkit", "scripts"))
from voice import gen_ts, resolve_tts  # noqa: E402


def test_gen_ts_exports_narration_and_cue():
    ts = gen_ts({"scan": {"dur": 41.2, "starts": [0.0, 1.5], "durs": [1.2, 3.0]}})
    assert "export const NARRATION" in ts
    assert "export const cue" in ts
    assert '"scan": {"dur": 41.2, "starts": [0.0, 1.5], "durs": [1.2, 3.0]}' in ts


def test_gen_ts_is_sorted_and_stable():
    a = gen_ts({"b": {"dur": 1, "starts": [0], "durs": [1]}, "a": {"dur": 2, "starts": [0], "durs": [2]}})
    b = gen_ts({"a": {"dur": 2, "starts": [0], "durs": [2]}, "b": {"dur": 1, "starts": [0], "durs": [1]}})
    assert a == b and a.index('"a"') < a.index('"b"')


def test_resolve_tts_precedence():
    profile = {"voice": "en-US-AvaNeural", "rate": "-7%"}
    assert resolve_tts({}, profile, {}) == {"engine": "edge", "voice": "en-US-AvaNeural", "rate": "-7%"}
    narr = {"tts": {"engine": "kokoro", "voice": "af_heart", "speed": 0.93}}
    assert resolve_tts(narr, profile, {})["engine"] == "kokoro"
    cli = {"engine": "chatterbox", "voice": "default"}
    got = resolve_tts(narr, {**profile, "tts": {"engine": "edge"}}, cli)
    assert got["engine"] == "chatterbox" and got["voice"] == "default" and got["speed"] == 0.93
