"""Text-to-speech using Microsoft Edge's free online voices. No API key needed."""

import asyncio
import re

import edge_tts


async def _synthesize(text, voice):
    audio = b""
    async for chunk in edge_tts.Communicate(text, voice).stream():
        if chunk["type"] == "audio":
            audio += chunk["data"]
    return audio


def synthesize(text, voice="en-US-AnaNeural", timeout=15):
    """Return MP3 bytes for the text, or None if the voice service fails or is too slow."""
    text = re.sub(r"[*_#`]", "", text)  # don't read markdown symbols out loud
    try:
        # edge-tts can hang well past its own timeouts when the service is unreachable.
        return asyncio.run(asyncio.wait_for(_synthesize(text, voice), timeout)) or None
    except Exception as e:
        print(f"Text-to-speech error: {e!r}")
        return None
