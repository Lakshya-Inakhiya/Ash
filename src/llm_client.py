"""Gemini client: chat replies and speech-to-text."""

from google import genai
from google.genai import errors, types


class LLMClient:
    def __init__(self, config, api_key):
        cfg = config["llm"]
        self.client = genai.Client(api_key=api_key)
        self.model = self._resolve_model(cfg["model"])
        self.chat_config = types.GenerateContentConfig(
            system_instruction=cfg["system_instruction"],
            max_output_tokens=cfg["max_tokens"],
            temperature=0.7,
        )
        self.reset_conversation()
        print(f"Gemini ready ({self.model})")

    def _resolve_model(self, wanted):
        """Use the configured model, or fall back to any available Flash model.

        Gemini models get retired often, so a stale name in settings.yaml
        shouldn't stop the robot from working.
        """
        try:
            self.client.models.get(model=wanted)
            return wanted
        except errors.ClientError as e:
            if e.code != 404:
                raise
        flash = [
            m.name.removeprefix("models/")
            for m in self.client.models.list()
            if "flash" in m.name
            and "generateContent" in (m.supported_actions or [])
            and not any(tag in m.name for tag in ("image", "tts", "live", "lite"))
        ]
        if not flash:
            raise RuntimeError(f"Model '{wanted}' not found and no Flash model available")
        # Prefer stable models, then the highest version.
        best = max(flash, key=lambda name: ("preview" not in name and "exp" not in name, name))
        print(f"Model '{wanted}' not found, using '{best}'")
        return best

    def reset_conversation(self):
        self.chat = self.client.chats.create(model=self.model, config=self.chat_config)

    def ask(self, prompt):
        if not prompt or not prompt.strip():
            return "I didn't catch that. Could you repeat?"
        try:
            answer = (self.chat.send_message(prompt).text or "").strip()
            return answer or "Sorry, I don't have an answer for that."
        except Exception as e:
            print(f"Gemini error: {e}")
            return "Sorry, I had trouble thinking of a response."

    def transcribe(self, wav_bytes, language="en"):
        """Return the words spoken in a WAV clip, or '' if there were none."""
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    f"Transcribe the speech in this audio (language: {language}). "
                    "Reply with only the words spoken. If there is no clear speech, reply with nothing.",
                    types.Part.from_bytes(data=wav_bytes, mime_type="audio/wav"),
                ],
                config=types.GenerateContentConfig(temperature=0),
            )
            return (response.text or "").strip()
        except Exception as e:
            print(f"Transcription error: {e}")
            return ""


if __name__ == "__main__":
    from utils import get_api_key, load_config

    client = LLMClient(load_config(), get_api_key())
    for q in ["What is your name?", "Tell me a fun fact about robots."]:
        print(f"Q: {q}\nA: {client.ask(q)}\n")
