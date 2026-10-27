"""Config and API key loading."""

import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_config(path="config/settings.yaml"):
    with open(PROJECT_ROOT / path) as f:
        return yaml.safe_load(f)


def get_api_key():
    load_dotenv(PROJECT_ROOT / ".env")
    key = os.getenv("GEMINI_API_KEY")
    if not key or key == "your_api_key_here":
        raise ValueError(
            "GEMINI_API_KEY not set. Copy .env.example to .env and add your key "
            "from https://aistudio.google.com/apikey"
        )
    return key
