# Ash Robot - Quick Usage Guide

## Starting Ash

### Voice Mode (Default)
```bash
python3 src/main.py
```
- Ash will listen for your voice
- Speak when you see "Listening..."

### Text-Only Mode
```bash
python3 src/main.py --text
```
- Type your questions instead of speaking
- Great for quiet environments or testing

### Help
```bash
python3 src/main.py --help
```

---

## During Interaction

### Commands You Can Type

| Command | What It Does |
|---------|-------------|
| `quit`, `exit`, `bye` | Exit Ash gracefully |
| `text` | Switch to text input mode |
| `voice` | Switch back to voice mode |
| `Ctrl+C` | Emergency exit |

### Switching Modes

**Start with voice, switch to text:**
```
[Listening...]
(Press Ctrl+C to interrupt)
You: text
✓ Switched to TEXT INPUT mode
```

**Switch back to voice:**
```
You: voice
✓ Switched to VOICE INPUT mode
```

---

## Example Sessions

### Voice Interaction
```
[Listening...] (speak now)
(You speak: "What is the weather today?")
✓ Recognized: what is the weather today
User: what is the weather today
Ash: I don't have access to real-time weather data...
```

### Text Interaction
```
You: What is 2 + 2?
User: What is 2 + 2?
Ash: The answer is 4.
```

### Exiting
```
You: quit
User: quit
Ash: Goodbye! Have a great day!
(Ash shuts down cleanly)
```

---

## Tips

- **Voice mode**: Wait for "Listening..." before speaking
- **Text mode**: More reliable, no audio issues
- **Quiet exit**: Type `quit` instead of Ctrl+C
- **Mode switching**: Works anytime during conversation
- **Face window**: Watch expressions change in real-time!

---

## Troubleshooting

**Voice not working?**
- Try text mode: `python3 src/main.py --text`
- Or type `text` during interaction

**Can't exit?**
- Type: `quit`, `exit`, or `bye`
- Press: `Ctrl+C` (may need twice)

**Want to test without voice?**
```bash
python3 src/main.py --text
```

---

## Quick Reference

```bash
# Start voice mode
python3 src/main.py

# Start text mode  
python3 src/main.py --text

# Get help
python3 src/main.py --help
```

**Interactive commands:**
- `quit` / `exit` / `bye` - Exit
- `text` - Text mode
- `voice` - Voice mode
- `Ctrl+C` - Force quit
