"""Ash on a Raspberry Pi: LCD face, servo arms, microphone and speaker.

    python -m hardware.main          # talk to it
    python -m hardware.main --text   # type instead
"""

import argparse
import sys
import time

from ash.brain import GESTURES, Brain
from ash.config import api_key, load_config
from ash.llm import LLM
from hardware.audio_io import AudioIO
from hardware.face_display import FaceDisplay
from hardware.gestures import ServoController

QUIT_WORDS = {"quit", "exit", "bye", "goodbye", "stop"}


class Robot:
    def __init__(self, text_mode=False):
        brain_config, config = load_config(), load_config("hardware/settings.yaml")
        key = api_key()
        if not key:
            sys.exit("GROQ_API_KEY not set. Copy .env.example to .env and add your key.")
        llm = LLM(key, **brain_config["llm"])
        self.brain = Brain(llm)
        self.history = []
        self.display = FaceDisplay(config)
        self.arms = ServoController(config["servos"], brain_config["gestures"])
        self.audio = AudioIO(config["audio"], brain_config["voice"], llm.transcribe)
        self.use_voice = self.audio.microphone_available and not text_mode
        self.cooldown = config["cooldown_period"]

    def listen(self):
        self.display.set_expression("listening")
        if self.use_voice:
            return self.audio.listen()
        try:
            return input("You: ").strip()
        except EOFError:
            return "quit"

    def handle(self, text):
        """Respond to one input. Returns False when it's time to stop."""
        command = text.lower().strip()
        if command in QUIT_WORDS:
            self.display.set_expression("happy")
            self.audio.speak("Goodbye! Have a great day!")
            return False
        if command in ("text", "voice"):
            self.use_voice = command == "voice" and self.audio.microphone_available
            print("Voice input" if self.use_voice else "Text input")
        elif command == "demo":
            for gesture in GESTURES:
                print(f"-> {gesture}")
                self.arms.perform(gesture)
        else:
            self.display.set_expression("thinking")
            reaction = self.brain.respond(text, self.history)
            self.history += [{"role": "user", "content": text}, {"role": "assistant", "content": reaction.reply}]
            self.display.set_expression("speaking")
            self.arms.perform(reaction.gesture)
            self.audio.speak(reaction.reply)
            self.display.set_expression(reaction.face)
            time.sleep(self.cooldown)
        return True

    def run(self):
        print("Say or type 'quit' to exit, 'demo' for gestures, 'text'/'voice' to switch input.")
        try:
            self.display.set_expression("happy")
            self.arms.perform("wave")
            self.audio.speak("Hello! I am Ash. I am ready to assist you.")
            while True:
                text = self.listen()
                if text:
                    print(f"You: {text}")
                    if not self.handle(text):
                        break
        except KeyboardInterrupt:
            print()
        finally:
            self.arms.close()
            self.audio.close()
            self.display.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ash robot on a Raspberry Pi")
    parser.add_argument("--text", action="store_true", help="type instead of talking")
    Robot(text_mode=parser.parse_args().text).run()
