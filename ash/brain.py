"""Ash's brain: what to say, which face to show and how to move.

It knows nothing about screens or motors, so the same brain drives both the
web avatar (app.py) and the Raspberry Pi robot (hardware/).
"""

import re
from dataclasses import dataclass

FACES = ("neutral", "happy", "sad", "listening", "thinking", "speaking", "error")
GESTURES = ("wave", "arms_up", "point")

GREETINGS = {"hello", "hi", "hey", "hiya", "greetings", "wave"}
CELEBRATIONS = ("yay", "awesome", "great", "celebrat", "congrat", "hooray", "excellent",
                "amazing", "fantastic", "passed", "i won")
QUESTION_STARTS = ("what", "why", "how", "when", "where", "who", "explain", "tell me", "can you")
SAD_WORDS = ("sad", "upset", "failed", "lonely", "bad day", "tired", "stressed", "lost my")


@dataclass
class Reaction:
    reply: str
    face: str = "happy"
    gesture: str | None = None


def pick_gesture(text):
    text = text.lower()
    # Match whole words so "this" doesn't count as "hi".
    if GREETINGS & set(re.findall(r"[a-z]+", text)):
        return "wave"
    if any(word in text for word in CELEBRATIONS):
        return "arms_up"
    if text.startswith(QUESTION_STARTS) or "?" in text:
        return "point"
    return None


def pick_face(text):
    return "sad" if any(word in text.lower() for word in SAD_WORDS) else "happy"


def gesture_poses(gesture, angles):
    """A gesture as a list of (left, right) arm angles. None means "at rest"."""
    return {
        "wave": [(angles["wave_start"], None), (angles["wave_end"], None)] * 3,
        "arms_up": [(angles["arms_up"], angles["arms_up"])],
        "point": [(None, angles["point_up"])],
    }.get(gesture, [])


class Brain:
    def __init__(self, llm):
        self.llm = llm

    def respond(self, text, history=()):
        """history: earlier messages as {"role": "user" | "assistant", "content": str}."""
        try:
            reply = self.llm.reply([*history, {"role": "user", "content": text}])
        except Exception as e:
            print(f"Gemini error: {e!r}")
            if getattr(e, "code", None) == 429:  # free-tier rate limit or daily quota
                return Reaction("I've used up my free thinking for now. Try again in a minute, "
                                "or add your own Gemini key below.", "error")
            return Reaction("Sorry, my brain glitched. Try again in a moment.", "error")
        return Reaction(reply, pick_face(text), pick_gesture(text))
