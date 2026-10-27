# Ash

A little robot you can talk to. Type or speak, and Ash answers using Google Gemini, then reacts with its face and arms: it waves when you say hi, points when you ask a question, and cheers when you share good news.

**Try it:** _live demo link goes here once deployed_

![Ash waving back after being greeted](docs/screenshot.png)

Ash started as a physical robot on a Raspberry Pi, with an LCD face and servo motor arms. I later redesigned it so the same brain can drive either that robot or an animated web version that anyone can try in a browser.

## How it works

```
 you ──► speech-to-text ──► Brain ──► reply + face + gesture ──► Body
        (Gemini)            (ash/brain.py)                       ├─ web avatar (app.py)
                                                                 └─ Raspberry Pi robot (hardware/)
```

- **Brain** (`ash/brain.py`) sends the conversation to Gemini and decides how Ash should react: which face to show and which gesture to make. It knows nothing about screens or motors.
- **Bodies** turn that reaction into something you can see. The web body draws Ash as an animated SVG. The hardware body shows images on an LCD and moves real servos. Gestures are defined once, as servo angles, and both bodies play them.
- **Speech:** Gemini transcribes your voice, and Ash replies using Microsoft Edge's free text-to-speech voices.
- **Model fallback:** Google retires Gemini models often. If the configured model disappears, Ash picks the newest stable Flash model instead of crashing.

![Ash's seven faces](docs/faces.png)

## Run it locally

You need Python 3.10+ and a free Gemini API key from [aistudio.google.com/apikey](https://aistudio.google.com/apikey).

```bash
git clone https://github.com/Lakshya-Inakhiya/Ash.git
cd Ash
python -m venv venv
venv/bin/pip install -r requirements.txt     # on Windows: venv\Scripts\pip
cp .env.example .env                         # then paste your key into .env
venv/bin/python app.py
```

Open http://127.0.0.1:7860 and say hi.

Run the tests with `venv/bin/pip install pytest && venv/bin/pytest`.

## Deploy your own copy

The app runs for free on [Hugging Face Spaces](https://huggingface.co/spaces). GitHub Actions runs the tests on every push and redeploys the Space when `main` changes.

1. Create a Space on Hugging Face (SDK: Gradio, hardware: free CPU).
2. In the Space's **Settings → Variables and secrets**, add a secret `GEMINI_API_KEY` with your key.
3. Create a Hugging Face access token with write permission at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).
4. In this GitHub repo's **Settings → Secrets and variables → Actions**, add a secret `HF_TOKEN` with that token and a variable `HF_SPACE` set to `your-hf-username/your-space-name`.
5. Push to `main`. The Space updates in a minute or two.

Visitors use your key, so they don't need one. If your free quota runs out, they can paste their own key in the app.

## Project layout

```
app.py              web app (Gradio)
ash/
  brain.py          decides what to say, which face to show, how to move
  llm.py            Gemini client: replies, speech-to-text, model fallback
  avatar.py         draws Ash as an animated SVG
  voice.py          text-to-speech
config/settings.yaml   Gemini model, personality, voice, gesture angles
hardware/           the original Raspberry Pi robot (see hardware/README.md)
tests/              pytest tests
```

## Built with

Python, Gradio, Google Gemini API, edge-tts, GitHub Actions, Hugging Face Spaces. The hardware version adds a Raspberry Pi 5, an SPI LCD driver written from scratch, and PCA9685 servo control.
