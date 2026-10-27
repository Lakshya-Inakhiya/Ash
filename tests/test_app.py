import app


def test_asks_for_a_key_when_none_is_set(monkeypatch):
    monkeypatch.setattr(app, "api_key", lambda: None)
    monkeypatch.setattr(app, "save_voice", lambda text: None)
    history, _, face, _, _ = list(app.respond({"text": "hi"}, [], ""))[-2]  # last update only adds the voice
    assert "API key" in history[-1]["content"]
    assert "Ash looking error" in face


def test_full_reply(monkeypatch):
    class FakeGemini:
        def __init__(self, key, **settings):
            pass

        def reply(self, history):
            return "Hello, human!"

    monkeypatch.setattr(app, "Gemini", FakeGemini)
    monkeypatch.setattr(app, "save_voice", lambda text: None)
    updates = list(app.respond({"text": "Hi Ash"}, [], "my-key"))
    assert "Ash looking thinking" in updates[0][2]
    history, _, face, _, _ = updates[-2]
    assert history == [{"role": "user", "content": "Hi Ash"}, {"role": "assistant", "content": "Hello, human!"}]
    assert "Ash looking happy" in face and "-left {" in face  # waves back
