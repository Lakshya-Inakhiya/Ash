"""AI client for chat replies and speech-to-text.

Uses Groq's free API by default. Groq speaks the same API as OpenAI, so any
OpenAI-compatible provider works by changing base_url and models in
config/settings.yaml.
"""

import time

from openai import OpenAI

TIMEOUT_SECONDS = 20
# Worth trying the next model for these: not found, rate-limited, or the server is struggling.
RETRYABLE_STATUS = {404, 429, 500, 502, 503, 504}
_available_models = {}


def status_of(error):
    return getattr(error, "status_code", None)


def is_retryable(error):
    name = type(error).__name__.lower()
    return status_of(error) in RETRYABLE_STATUS or "timeout" in name or "connection" in name


def available(client, wanted):
    """Keep the wanted models the provider still offers, in order.

    Providers retire models often, so a stale name in the settings shouldn't
    break Ash. If none are left, fall back to whatever chat model exists.
    """
    try:
        offered = {m.id for m in client.models.list()}
    except Exception as e:
        print(f"Couldn't list models ({e!r}); trying the configured ones anyway.")
        return list(wanted)
    models = [m for m in wanted if m in offered]
    if not models:
        chat = sorted(m for m in offered if not any(tag in m for tag in ("whisper", "guard", "tts", "embed")))
        models = chat[-1:]
        print(f"None of {wanted} are available, using {models}")
    return models


class LLM:
    def __init__(self, api_key, base_url, models, speech_models=(), system_instruction=None):
        self.client = OpenAI(api_key=api_key, base_url=base_url, timeout=TIMEOUT_SECONDS, max_retries=0)
        key = (base_url, tuple(models))
        if key not in _available_models:
            _available_models[key] = available(self.client, models)
            print(f"Chat models: {_available_models[key]}")
        self.models = _available_models[key]
        self.speech_models = list(speech_models)
        self.system_instruction = system_instruction

    def _try_models(self, models, call):
        """Run call(model) on each model in turn until one works."""
        for i, model in enumerate(models):
            start = time.monotonic()
            try:
                result = call(model)
                print(f"{model} answered in {time.monotonic() - start:.1f}s")
                return result
            except Exception as e:
                if not is_retryable(e) or i == len(models) - 1:
                    raise
                print(f"{model} failed after {time.monotonic() - start:.1f}s ({e!r}); trying the next model.")

    def reply(self, history):
        """history: messages as {"role": "user" | "assistant", "content": str}."""
        messages = [{"role": "system", "content": self.system_instruction}, *history]
        response = self._try_models(
            self.models,
            lambda model: self.client.chat.completions.create(model=model, messages=messages, temperature=0.7),
        )
        return (response.choices[0].message.content or "").strip() or "Hmm, I don't have an answer for that."

    def transcribe(self, audio, filename="speech.wav"):
        """Return the words spoken in an audio clip, or '' if there were none."""
        try:
            result = self._try_models(
                self.speech_models,
                lambda model: self.client.audio.transcriptions.create(model=model, file=(filename, audio)),
            )
            return (result.text or "").strip()
        except Exception as e:
            print(f"Transcription error: {e!r}")
            return ""
