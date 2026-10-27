from types import SimpleNamespace

import pytest
from google.genai import errors

from ash.llm import resolve_model, to_contents


def model(name, actions=("generateContent",)):
    return SimpleNamespace(name=f"models/{name}", supported_actions=list(actions))


class FakeModels:
    def __init__(self, available, error_code=404):
        self.available, self.error_code = available, error_code

    def get(self, model):
        if model not in self.available:
            raise errors.ClientError(self.error_code, {"error": {"message": "nope"}})

    def list(self):
        return [model(name) for name in self.available] + [model("text-embedding", ("embedContent",))]


def client(available, error_code=404):
    return SimpleNamespace(models=FakeModels(available, error_code))


def test_keeps_configured_model_when_it_exists():
    assert resolve_model(client(["gemini-flash-latest"]), "gemini-flash-latest") == "gemini-flash-latest"


def test_falls_back_to_newest_stable_flash():
    available = ["gemini-3.5-flash", "gemini-3.8-flash-preview", "gemini-3.5-flash-lite", "gemini-3.5-flash-image"]
    assert resolve_model(client(available), "gemini-2.0-flash-exp") == "gemini-3.5-flash"


def test_other_errors_are_not_hidden():
    with pytest.raises(errors.ClientError):
        resolve_model(client([], error_code=400), "gemini-flash-latest")  # e.g. a bad API key


def test_to_contents_maps_roles():
    contents = to_contents([{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hello"}])
    assert [c.role for c in contents] == ["user", "model"]
    assert contents[1].parts[0].text == "hello"
