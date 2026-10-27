"""Gemini client for chat replies and speech-to-text. The free API tier is enough."""

import time

from google import genai
from google.genai import errors, types

TIMEOUT_SECONDS = 20
# Worth trying another model for these: not found, rate-limited, overloaded or broken.
RETRYABLE_CODES = {404, 429, 500, 503}
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
    def __init__(self, api_key, model="gemini-flash-latest", system_instruction=None, backup_models=()):
        self.client = genai.Client(api_key=api_key, http_options=types.HttpOptions(timeout=TIMEOUT_SECONDS * 1000))
        if model not in _resolved_models:
            _resolved_models[model] = resolve_model(self.client, model)
            print(f"Using Gemini model: {_resolved_models[model]}")
        self.model = _resolved_models[model]
        self.backup_models = [m for m in backup_models if m != self.model]
        self.config = types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.7)

    def _generate(self, contents, config):
        """Call Gemini, moving on to a backup model if one is overloaded, out of quota or too slow.

        Each model has its own capacity and free-tier limits, so a backup often
        works when the main model doesn't.
        """
        models = [self.model, *self.backup_models]
        for i, model in enumerate(models):
            start = time.monotonic()
            try:
                response = self.client.models.generate_content(model=model, contents=contents, config=config)
                print(f"Gemini ({model}) replied in {time.monotonic() - start:.1f}s")
                return response
            except Exception as e:
                retryable = getattr(e, "code", None) in RETRYABLE_CODES or "timeout" in type(e).__name__.lower()
                if not retryable or i == len(models) - 1:
                    raise
                print(f"Gemini ({model}) failed after {time.monotonic() - start:.1f}s: {e!r}. Trying a backup model.")

    def reply(self, history):
        response = self._generate(to_contents(history), self.config)
        return (response.text or "").strip() or "Hmm, I don't have an answer for that."

    def transcribe(self, audio, mime_type="audio/wav"):
        """Return the words spoken in an audio clip, or '' if there were none."""
        try:
            response = self._generate(
                [
                    "Transcribe the speech in this audio. Reply with only the words spoken. "
                    "If there is no clear speech, reply with nothing.",
                    types.Part.from_bytes(data=audio, mime_type=mime_type),
                ],
                types.GenerateContentConfig(temperature=0),
            )
            return (response.text or "").strip()
        except Exception as e:
            print(f"Transcription error: {e}")
            return ""
