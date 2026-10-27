#!/usr/bin/env python3
"""Ash desktop robot: listen, ask Gemini, answer with a face, voice and arm gestures.

    python3 src/main.py          # voice input (falls back to typing without a mic)
    python3 src/main.py --text   # typed input only
"""

import argparse
import re
import sys
import time

from audio_io import AudioIO
from face_display import FaceDisplay
from gestures import ServoController
from llm_client import LLMClient
from utils import get_api_key, load_config

QUIT_WORDS = {"quit", "exit", "bye", "goodbye", "stop"}
DEMO_WORDS = {"gestures", "demo", "show gestures", "test gestures", "demo gestures"}
GREETINGS = ("hello", "hi", "hey", "greet", "wave")
CELEBRATIONS = ("yay", "awesome", "great", "celebrate", "congrat", "hooray", "excellent", "amazing", "fantastic")
QUESTIONS = ("what", "why", "how", "when", "where", "who", "explain", "tell me")


class Ash:
    def __init__(self, text_mode=False):
        self.config = load_config()
        try:
            self.llm = LLMClient(self.config, get_api_key())
        except ValueError as e:
            sys.exit(str(e))
        self.display = FaceDisplay(self.config)
        self.arms = ServoController(self.config)
        self.audio = AudioIO(self.config, transcriber=self.llm.transcribe)
        self.use_voice = self.audio.microphone_available and not text_mode
        self.cooldown = self.config["main"]["cooldown_period"]

    def say(self, face, text, gesture=None):
        self.display.set_expression(face)
        if gesture:
            gesture()
        self.audio.speak(text)

    def pick_gesture(self, text):
        words = set(re.findall(r"[a-z']+", text))
        if words & set(GREETINGS):
            return self.arms.wave
        if any(w in text for w in CELEBRATIONS):
            return self.arms.arms_up
        if text.startswith(QUESTIONS) or "?" in text:
            return self.arms.point
        return None

    def demo(self):
        for face, gesture in [("neutral", self.arms.neutral), ("happy", self.arms.arms_up),
                              ("neutral", self.arms.arms_down), ("thinking", self.arms.point),
                              ("happy", self.arms.wave)]:
            print(f"-> {gesture.__name__}")
            self.display.set_expression(face)
            gesture()
            time.sleep(1.5)
        self.arms.neutral()

    def listen(self):
        if self.use_voice:
            return self.audio.listen()
        try:
            return input("You: ").strip()
        except EOFError:
            return "quit"

    def handle(self, user_input):
        """Respond to one input. Returns False when it's time to stop."""
        command = user_input.lower().strip()
        if command in QUIT_WORDS:
            self.say("happy", "Goodbye! Have a great day!")
            return False
        if command == "text":
            self.use_voice = False
            print("Switched to text input")
        elif command == "voice":
            self.use_voice = self.audio.microphone_available
            print("Switched to voice input" if self.use_voice else "No microphone available")
        elif command in DEMO_WORDS:
            self.demo()
        else:
            gesture = self.pick_gesture(command)
            self.display.set_expression("thinking")
            self.arms.point()
            reply = self.llm.ask(user_input)
            self.say("speaking", reply, gesture if gesture != self.arms.point else None)
            self.display.set_expression("happy")
            if gesture not in (self.arms.wave, self.arms.arms_up):
                self.arms.arms_up()
            time.sleep(self.cooldown)
        return True

    def run(self):
        print("Say or type 'quit' to exit, 'demo' for gestures, 'text'/'voice' to switch input.")
        try:
            self.display.set_expression(self.config["main"]["startup_expression"])
            self.arms.neutral()
            self.say("happy", "Hello! I am Ash. I am ready to assist you.", lambda: self.arms.wave(2))
            while True:
                self.display.set_expression("listening")
                self.arms.neutral()
                user_input = self.listen()
                if not user_input:
                    continue
                print(f"You: {user_input}")
                try:
                    if not self.handle(user_input):
                        break
                except Exception as e:
                    print(f"Error: {e}")
                    self.say("error", "Sorry, I encountered an error.")
        except KeyboardInterrupt:
            print()
        finally:
            self.arms.close()
            self.audio.close()
            self.display.close()


def main():
    parser = argparse.ArgumentParser(description="Ash desktop AI robot")
    parser.add_argument("--text", action="store_true", help="type instead of talking")
    Ash(text_mode=parser.parse_args().text).run()


if __name__ == "__main__":
    main()
