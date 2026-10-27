from types import SimpleNamespace

import pytest
from google.genai import errors

from ash.llm import Gemini, resolve_model, to_contents


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


class FlakyModels:
    """Fails with the given error for the listed models, answers for the rest."""

    def __init__(self, failures):
        self.failures, self.tried = failures, []

    def generate_content(self, model, contents, config):
        self.tried.append(model)
        if model in self.failures:
            raise self.failures[model]
        return SimpleNamespace(text=f"answer from {model}")


def gemini(failures, backups=("backup-1", "backup-2")):
    g = Gemini.__new__(Gemini)
    g.client = SimpleNamespace(models=FlakyModels(failures))
    g.model, g.backup_models, g.config = "main", list(backups), None
    return g


def test_uses_backup_model_when_main_is_overloaded():
    g = gemini({"main": errors.ServerError(503, {"error": {"message": "high demand"}})})
    assert g.reply([{"role": "user", "content": "hi"}]) == "answer from backup-1"


def test_keeps_trying_backups_until_one_works():
    quota = errors.ClientError(429, {"error": {"message": "quota"}})
    g = gemini({"main": quota, "backup-1": quota})
    assert g.reply([{"role": "user", "content": "hi"}]) == "answer from backup-2"


def test_does_not_retry_errors_a_backup_cannot_fix():
    g = gemini({"main": errors.ClientError(400, {"error": {"message": "bad request"}})})
    with pytest.raises(errors.ClientError):
        g.reply([{"role": "user", "content": "hi"}])
    assert g.client.models.tried == ["main"]


def test_raises_last_error_when_every_model_fails():
    busy = errors.ServerError(503, {"error": {"message": "high demand"}})
    g = gemini({"main": busy, "backup-1": busy, "backup-2": busy})
    with pytest.raises(errors.ServerError):
        g.reply([{"role": "user", "content": "hi"}])
