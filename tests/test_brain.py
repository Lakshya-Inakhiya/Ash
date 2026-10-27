import pytest
from google.genai import errors

from ash.brain import Brain, gesture_poses, pick_face, pick_gesture
from ash.config import load_config

ANGLES = load_config()["gestures"]


@pytest.mark.parametrize("text, gesture", [
    ("Hello Ash", "wave"),
    ("hey, how are you?", "wave"),
    ("This is a test", None),  # "this" contains "hi" but isn't a greeting
    ("I passed my exam!", "arms_up"),
    ("What is a black hole", "point"),
    ("tell me a joke", "point"),
    ("is it raining?", "point"),
    ("ok", None),
])
def test_pick_gesture(text, gesture):
    assert pick_gesture(text) == gesture


def test_pick_face():
    assert pick_face("I had a bad day") == "sad"
    assert pick_face("Tell me a joke") == "happy"


def test_gesture_poses():
    assert len(gesture_poses("wave", ANGLES)) == 6
    assert gesture_poses("point", ANGLES) == [(None, ANGLES["point_up"])]
    assert gesture_poses(None, ANGLES) == []


class FakeLLM:
    def __init__(self, fail=None):
        self.fail = fail
        self.seen = None

    def reply(self, history):
        if self.fail:
            raise self.fail
        self.seen = history
        return "Hi there!"


def test_respond_sends_history_and_picks_reaction():
    llm = FakeLLM()
    earlier = [{"role": "user", "content": "yo"}, {"role": "assistant", "content": "Hello!"}]
    reaction = Brain(llm).respond("Hello again", earlier)
    assert (reaction.reply, reaction.face, reaction.gesture) == ("Hi there!", "happy", "wave")
    assert llm.seen == [*earlier, {"role": "user", "content": "Hello again"}]


def test_respond_shows_error_face_when_gemini_fails():
    reaction = Brain(FakeLLM(fail=RuntimeError("boom"))).respond("Hello")
    assert reaction.face == "error"
    assert reaction.gesture is None
    assert "glitched" in reaction.reply


def test_respond_explains_quota_limits():
    quota = errors.ClientError(429, {"error": {"message": "RESOURCE_EXHAUSTED"}})
    assert "own Gemini key" in Brain(FakeLLM(fail=quota)).respond("Hello").reply


def test_respond_explains_timeouts():
    class ReadTimeout(Exception):
        pass

    assert "too slowly" in Brain(FakeLLM(fail=ReadTimeout())).respond("Hello").reply
