#!/bin/bash
# Quick activation script for Ash robot development

# Activate virtual environment
source venv/bin/activate

# Set prompt to show we're in Ash venv
export PS1="(ash) \[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ "

echo "╔════════════════════════════════════════════╗"
echo "║     Ash Robot Virtual Environment         ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "Virtual environment activated!"
echo ""
echo "Quick Commands:"
echo "  python3 src/main.py           - Run Ash"
echo "  python3 src/face_display.py   - Test display"
echo "  python3 src/gestures.py       - Test servos"
echo "  python3 src/audio_io.py       - Test audio"
echo "  python3 src/llm_client.py     - Test Gemini API"
echo ""
echo "To deactivate: deactivate"
echo ""

# Start a new shell with the activated environment
exec $SHELL

