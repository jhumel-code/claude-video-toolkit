import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skills", "video-toolkit", "scripts"))
from narration_lint import lint  # noqa: E402


def rules(text):
    return {(level, msg.split(":")[0]) for level, msg in lint(text)}


def test_em_dash_is_error():
    assert ("error", "em dash") in rules("It works — mostly.")


def test_structural_label_is_error():
    assert ("error", "structural label") in rules("Act one. The scan runs.")


def test_long_sentence_warns():
    assert ("warn", "long sentence") in rules(" ".join(["word"] * 27) + ".")


def test_colon_reveal_warns():
    assert ("warn", "colon reveal") in rules("Everything compiles from one place: the contract.")


def test_negative_parallel_warns():
    assert ("warn", "not X; Y") in rules("Most failures are not exploits; they are misconfigurations.")


def test_filler_word_warns():
    assert ("warn", "filler word") in rules("And crucially, the policy lives outside.")


def test_semicolon_warns():
    assert ("warn", "semicolon") in rules("It checks tools; it also checks guards.")


def test_no_contractions_warns():
    assert ("warn", "no contractions") in rules(" ".join(["The scan reads the code."] * 13))


def test_list_stacking_warns():
    assert ("warn", "list stacking") in rules(
        "It inventories every tool, agent, subagent, skill, server, and guard, then checks them.")


def test_possessive_is_not_a_contraction():
    text = " ".join(["The agent's code is read by the scan."] * 9)
    assert ("warn", "no contractions") in rules(text)


def test_clean_human_text_passes():
    assert lint("We'll start with the scan. It reads your agent's code. "
                "Then it checks each tool against a set of rules.") == []
