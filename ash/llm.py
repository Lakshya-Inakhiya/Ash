"""Gemini client for chat replies and speech-to-text. The free API tier is enough."""

from google import genai
from google.genai import errors, types

_resolved_models = {}


def resolve_model(client, wanted):
    """Use the configured model, or fall back to an available Flash model.

    Gemini models get retired often, so a stale name in the settings
    shouldn't break Ash.
    """
    try:
        client.models.get(model=wanted)
        return wanted
    except errors.ClientError as e:
        if e.code != 404:
            raise
    flash = [
        m.name.removeprefix("models/")
        for m in client.models.list()
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


def to_contents(history):
    return [
        types.Content(
            role="model" if message["role"] == "assistant" else "user",
            parts=[types.Part.from_text(text=message["content"])],
        )
        for message in history
    ]


class Gemini:
    def __init__(self, api_key, model="gemini-flash-latest", system_instruction=None):
        self.client = genai.Client(api_key=api_key)
        if model not in _resolved_models:
            _resolved_models[model] = resolve_model(self.client, model)
        self.model = _resolved_models[model]
        self.config = types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.7)

    def reply(self, history):
        response = self.client.models.generate_content(
            model=self.model, contents=to_contents(history), config=self.config
        )
        return (response.text or "").strip() or "Hmm, I don't have an answer for that."

    def transcribe(self, audio, mime_type="audio/wav"):
        """Return the words spoken in an audio clip, or '' if there were none."""
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    "Transcribe the speech in this audio. Reply with only the words spoken. "
                    "If there is no clear speech, reply with nothing.",
                    types.Part.from_bytes(data=audio, mime_type=mime_type),
                ],
                config=types.GenerateContentConfig(temperature=0),
            )
            return (response.text or "").strip()
        except Exception as e:
            print(f"Transcription error: {e}")
            return ""
