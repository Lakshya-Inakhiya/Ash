"""Ash on the web: talk or type to a little robot that answers using Gemini."""

import mimetypes
import os
import tempfile
import time
from pathlib import Path

import gradio as gr

from ash import avatar, voice
from ash.brain import Brain, gesture_poses
from ash.config import api_key, load_config
from ash.llm import Gemini

CONFIG = load_config()
MAX_INPUT_CHARS = 500
AUDIO_DIR = Path(tempfile.gettempdir()) / "ash-voice"


def save_voice(text):
    """Write Ash's spoken reply to an MP3 file for the audio player."""
    audio = voice.synthesize(text, CONFIG["voice"])
    if not audio:
        return None
    AUDIO_DIR.mkdir(exist_ok=True)
    for old in AUDIO_DIR.glob("*.mp3"):  # clean up replies older than 10 minutes
        if time.time() - old.stat().st_mtime > 600:
            old.unlink(missing_ok=True)
    path = AUDIO_DIR / f"{time.time_ns()}.mp3"
    path.write_bytes(audio)
    return str(path)


def respond(message, history, user_key):
    """Handle one message. Yields updates so the face changes while Ash works."""
    text = (message.get("text") or "").strip()
    recordings = message.get("files") or []
    box = gr.MultimodalTextbox(value=None, interactive=False)
    done = gr.MultimodalTextbox(value=None, interactive=True)

    def say(reply, face, poses=()):
        """Show the reply right away, then add the voice once it's ready."""
        new_history = history + [{"role": "assistant", "content": reply}]
        yield new_history, new_history, avatar.render(face, poses), None, done
        yield new_history, new_history, gr.skip(), save_voice(reply), done

    key = (user_key or "").strip() or api_key()
    if not key:
        yield from say("I need a Gemini API key to think. Add one under 'Use your own Gemini key'.", "error")
        return
    try:
        brain = Brain(Gemini(key, **CONFIG["llm"]))
    except Exception as e:
        print(f"Gemini setup failed: {e}")
        yield from say("That Gemini API key didn't work. Check it and try again.", "error")
        return

    if recordings and not text:
        yield history, history, avatar.render("listening"), None, box
        path = recordings[-1]
        text = brain.llm.transcribe(Path(path).read_bytes(), mimetypes.guess_type(path)[0] or "audio/wav")
        if not text:
            yield from say("I didn't catch that. Could you try again?", "neutral")
            return

    if not text:
        yield history, history, avatar.render("neutral"), None, done
        return

    previous = history
    history = history + [{"role": "user", "content": text[:MAX_INPUT_CHARS]}]
    yield history, history, avatar.render("thinking"), None, box

    reaction = brain.respond(history[-1]["content"], previous)
    yield from say(reaction.reply, reaction.face, gesture_poses(reaction.gesture, CONFIG["gestures"]))


with gr.Blocks(title="Ash") as demo:
    gr.Markdown(
        "# Ash\nA little robot you can talk to. Type, or press the mic and speak. "
        "Ash answers with Gemini and reacts with its face and arms. "
        "[Source on GitHub](https://github.com/Lakshya-Inakhiya/Ash)"
    )
    history = gr.State([])
    with gr.Row():
        with gr.Column(scale=2):
            face = gr.HTML(avatar.render("neutral"))
            speaker = gr.Audio(label="Ash's voice", autoplay=True, interactive=False)
        with gr.Column(scale=3):
            chat = gr.Chatbot(label="Conversation", height=430)
            box = gr.MultimodalTextbox(
                placeholder="Say hi to Ash...", sources=["microphone"], file_types=["audio"], show_label=False
            )
            gr.Examples(
                [{"text": "Hi Ash!"}, {"text": "Explain black holes like I'm five"}, {"text": "I passed my exam!"}],
                inputs=box,
            )
    with gr.Accordion("Use your own Gemini key", open=False):
        user_key = gr.Textbox(
            type="password", show_label=False,
            placeholder="Optional. Get a free key at aistudio.google.com/apikey. It's only used for your messages.",
        )

    box.submit(respond, [box, history, user_key], [history, chat, face, speaker, box])

CSS = ".ash-avatar svg { width: 100%; max-height: 420px; }"

if __name__ == "__main__":
    # Hosts like Render tell the app which port to use through $PORT.
    port = os.getenv("PORT")
    demo.launch(css=CSS, server_name="0.0.0.0" if port else None, server_port=int(port) if port else None)
