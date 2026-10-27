"""Microphone recording (stops when you stop talking) and text-to-speech."""

import io
import time
import wave

import numpy as np
import pygame

from ash.voice import synthesize

try:
    import sounddevice as sd
except OSError:  # PortAudio not installed
    sd = None

SAMPLE_RATE = 16000
BLOCK_SECONDS = 0.1


class AudioIO:
    def __init__(self, cfg, voice, transcriber=None):
        """transcriber: callable(wav_bytes) -> str, e.g. Gemini.transcribe."""
        self.timeout = cfg["timeout"]
        self.phrase_time_limit = cfg["phrase_time_limit"]
        self.silence_seconds = cfg.get("silence_seconds", 1.0)
        self.voice = voice
        self.transcriber = transcriber

        pygame.mixer.init()
        self.microphone_available = False
        self.threshold = cfg.get("silence_threshold", 500)
        try:
            if sd is None:
                raise RuntimeError("PortAudio not installed")
            # Calibrate against room noise so the silence detector isn't fooled by a fan.
            ambient = sd.rec(int(0.5 * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype="int16")
            sd.wait()
            self.threshold = max(self.threshold, 3 * _rms(ambient))
            self.microphone_available = True
            print(f"Microphone ready: {sd.query_devices(kind='input')['name']}")
        except Exception as e:
            print(f"No microphone ({e}); using text input.")

    def record(self):
        """Record from when speech starts until a pause. Returns int16 samples, or None."""
        block = int(BLOCK_SECONDS * SAMPLE_RATE)
        # Everything below counts blocks, not seconds, to avoid float drift.
        wait_limit = round(self.timeout / BLOCK_SECONDS)
        silence_limit = round(self.silence_seconds / BLOCK_SECONDS)
        length_limit = round(self.phrase_time_limit / BLOCK_SECONDS)
        chunks, started, silent, waited = [], False, 0, 0
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="int16", blocksize=block) as stream:
            while True:
                data, _ = stream.read(block)
                loud = _rms(data) > self.threshold
                if not started:
                    waited += 1
                    if loud:
                        started = True
                    elif waited >= wait_limit:
                        return None
                    else:
                        chunks = [data]  # keep one block of lead-in so the first word isn't clipped
                        continue
                chunks.append(data)
                silent = 0 if loud else silent + 1
                if silent >= silence_limit or len(chunks) >= length_limit:
                    return np.concatenate(chunks)

    def listen(self):
        """Return what the user said (or typed, without a mic). '' if nothing."""
        if not self.microphone_available or self.transcriber is None:
            try:
                return input("You: ").strip()
            except EOFError:
                return ""
        print("Listening...")
        samples = self.record()
        if samples is None:
            return ""
        print("Processing speech...")
        text = self.transcriber(_to_wav(samples))
        if text:
            print(f"Heard: {text}")
        return text

    def speak(self, text):
        if not text or not text.strip():
            return False
        print(f"Ash: {text}")
        mp3 = synthesize(text, self.voice)
        if not mp3:
            return False
        try:
            pygame.mixer.music.load(io.BytesIO(mp3), "mp3")
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            return True
        except Exception as e:
            print(f"Text-to-speech error: {e}")
            return False

    def close(self):
        pygame.mixer.quit()


def _rms(samples):
    return float(np.sqrt(np.mean(samples.astype(np.float32) ** 2))) if samples.size else 0.0


def _to_wav(samples):
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        w.writeframes(samples.tobytes())
    return buf.getvalue()


if __name__ == "__main__":
    from ash.config import api_key, load_config
    from ash.llm import Gemini

    brain_config = load_config()
    gemini = Gemini(api_key(), **brain_config["llm"])
    audio = AudioIO(load_config("hardware/settings.yaml")["audio"], brain_config["voice"], gemini.transcribe)
    audio.speak("Hello! Say something and I will repeat it.")
    heard = audio.listen()
    audio.speak(f"You said: {heard}" if heard else "I didn't hear anything.")
    audio.close()
