from types import SimpleNamespace

import pytest

from ash.llm import LLM, available, is_retryable


class APIError(Exception):
    def __init__(self, status_code):
        self.status_code = status_code


class APITimeoutError(Exception):
    pass


def model_list(*ids):
    return SimpleNamespace(models=SimpleNamespace(list=lambda: [SimpleNamespace(id=i) for i in ids]))


def test_keeps_wanted_models_that_exist_in_order():
    client = model_list("llama-3.1-8b-instant", "openai/gpt-oss-20b", "whisper-large-v3")
    assert available(client, ["openai/gpt-oss-20b", "retired-model", "llama-3.1-8b-instant"]) == [
        "openai/gpt-oss-20b", "llama-3.1-8b-instant"]


def test_falls_back_to_any_chat_model_when_all_are_retired():
    client = model_list("whisper-large-v3", "meta-llama/llama-guard-4", "qwen/qwen3-32b")
    assert available(client, ["retired-model"]) == ["qwen/qwen3-32b"]


def test_uses_configured_models_if_listing_fails():
    def broken():
        raise APITimeoutError()
    assert available(SimpleNamespace(models=SimpleNamespace(list=broken)), ["a", "b"]) == ["a", "b"]


@pytest.mark.parametrize("error, retryable", [
    (APIError(429), True), (APIError(503), True), (APIError(504), True), (APIError(404), True),
    (APITimeoutError(), True), (APIError(400), False), (APIError(401), False), (ValueError(), False),
])
def test_is_retryable(error, retryable):
    assert is_retryable(error) == retryable


class FlakyCompletions:
    """Fails with the given error for the listed models, answers for the rest."""

    def __init__(self, failures):
        self.failures, self.tried = failures, []

    def create(self, model, messages, temperature):
        self.tried.append(model)
        if model in self.failures:
            raise self.failures[model]
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=f"answer from {model}"))])


def llm(failures, models=("main", "backup-1", "backup-2")):
    client = LLM.__new__(LLM)
    client.client = SimpleNamespace(chat=SimpleNamespace(completions=FlakyCompletions(failures)))
    client.models, client.system_instruction = list(models), "Be Ash."
    return client


HI = [{"role": "user", "content": "hi"}]


def test_sends_personality_and_history():
    client = llm({})
    client.client.chat.completions.create = lambda model, messages, temperature: (
        SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=str(messages)))]))
    assert "'role': 'system', 'content': 'Be Ash.'" in client.reply(HI)


def test_uses_next_model_when_one_is_busy():
    assert llm({"main": APIError(503)}).reply(HI) == "answer from backup-1"


def test_keeps_trying_until_a_model_works():
    assert llm({"main": APIError(429), "backup-1": APITimeoutError()}).reply(HI) == "answer from backup-2"


def test_does_not_retry_errors_another_model_cannot_fix():
    client = llm({"main": APIError(401)})
    with pytest.raises(APIError):
        client.reply(HI)
    assert client.client.chat.completions.tried == ["main"]


def test_raises_when_every_model_fails():
    with pytest.raises(APIError):
        llm({m: APIError(503) for m in ("main", "backup-1", "backup-2")}).reply(HI)
