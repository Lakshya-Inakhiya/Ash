"""Settings and API key loading."""

import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent


def load_config(path="config/settings.yaml"):
    with open(ROOT / path) as f:
        return yaml.safe_load(f)


def api_key():
    """The Gemini key from .env (local) or the environment (e.g. a secret set on Render)."""
    load_dotenv(ROOT / ".env")
    key = os.getenv("GEMINI_API_KEY", "").strip()
    return key if key and key != "your_api_key_here" else None
