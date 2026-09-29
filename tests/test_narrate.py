import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skills", "video-toolkit", "scripts"))
from narrate import pick_tts  # noqa: E402

KOKORO = {"engine": "kokoro", "voice": "af_heart", "speed": 0.93}
PROFILE = {"tts": KOKORO, "voice": "en-US-AvaNeural", "rate": "-7%"}


def test_profile_tts_is_the_default():
    assert pick_tts({}, PROFILE, "en-US-AvaNeural", "-7%") == KOKORO


def test_spec_voice_or_rate_beats_profile_tts():
    assert pick_tts({"voice": "en-US-AndrewNeural"}, PROFILE, "en-US-AndrewNeural", "-7%") == {
        "engine": "edge", "voice": "en-US-AndrewNeural", "rate": "-7%"}
    assert pick_tts({"rate": "-10%"}, PROFILE, "en-US-AvaNeural", "-10%")["engine"] == "edge"


def test_spec_tts_beats_everything():
    spec = {"tts": {"engine": "chatterbox"}, "voice": "en-US-AndrewNeural"}
    assert pick_tts(spec, PROFILE, "en-US-AndrewNeural", "-7%") == {"engine": "chatterbox"}


def test_edge_when_no_tts_anywhere():
    assert pick_tts({}, {"voice": "en-US-AvaNeural"}, "en-US-AvaNeural", "+0%") == {
        "engine": "edge", "voice": "en-US-AvaNeural", "rate": "+0%"}
