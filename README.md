# Ash

A desktop robot built on a Raspberry Pi 5. You talk to it, it answers using Google Gemini, shows a face on a 3.5" LCD, and moves two servo arms.

Everything also runs on a laptop: the face appears in a window and gestures are just logged, so you can work on it without the hardware.

## Hardware

- Raspberry Pi 5 (a Pi 4 works too)
- 3.5" ILI9486 SPI LCD, 480×320 (goodtft MPI3501 or Waveshare 3.5" A)
- PCA9685 16-channel servo board and two MG995 servos
- 5V power supply for the servos, at least 3A
- USB microphone and a speaker

### Wiring

The LCD plugs straight onto header pins 1–26. It uses SPI0 plus GPIO 24 (DC), 25 (reset) and 18 (backlight).

| PCA9685 | Raspberry Pi |
|---|---|
| VCC | Pin 1 (3.3V) |
| GND | Pin 6 (GND) |
| SDA | Pin 3 (GPIO 2) |
| SCL | Pin 5 (GPIO 3) |
| V+ | Servo supply 5V |

Plug the left arm servo into channel 0 and the right arm into channel 1.

Two rules so you don't damage anything:

- **Never power the servos from the Pi's 5V pins.** MG995s can pull over 1A each.
- **Connect the servo supply's ground to the Pi's ground** as well as to the PCA9685. Without a shared ground the servos jitter or don't move at all.

You don't need the old `LCD-show` driver. It doesn't work on the Pi 5, and Ash drives the screen directly over SPI.

## Setup

```bash
git clone https://github.com/Lakshya-Inakhiya/Ash.git
cd Ash
./setup.sh
sudo reboot
```

`setup.sh` installs system packages, turns on I2C and SPI, creates a virtual environment, and asks for your Gemini API key. You can get a free key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey). The key is saved to `.env`, which git ignores.

On a Mac or PC, skip the script:

```bash
python3 -m venv venv
venv/bin/pip install -r requirements.txt
cp .env.example .env   # then add your key
```

## Running

```bash
venv/bin/python src/main.py          # talk to it
venv/bin/python src/main.py --text   # type instead
```

Ash records until you stop talking, sends the audio to Gemini for transcription, then speaks the reply. Say or type `demo` to see every gesture, `text` or `voice` to switch input, and `quit` to exit.

Each module can also run on its own, which helps when you're checking hardware one piece at a time:

```bash
venv/bin/python src/lcd_spi_driver.py   # flashes red, green, blue, white
venv/bin/python src/face_display.py     # cycles through the faces
venv/bin/python src/gestures.py         # runs every arm gesture
venv/bin/python src/audio_io.py         # speaks, listens, repeats what you said
venv/bin/python src/llm_client.py       # asks Gemini two questions
```

## Configuration

Settings are in `config/settings.yaml`: pins, servo angles, audio thresholds and the Gemini model. Faces are PNGs in `assets/faces/` (`happy`, `sad`, `neutral`, `listening`, `speaking`, `thinking`, `error`). Any size works, since they're scaled to 480×320.

## Troubleshooting

**Screen stays white or shows noise.** Check that SPI is on with `ls /dev/spidev0.0`. If you have a bare ILI9486 module rather than an MPI3501 or Waveshare board, set `register_width: 8`. If the image is garbled, lower `speed_hz`.

**Servos don't move.** Run `i2cdetect -y 1`. You should see `40`. If not, recheck SDA, SCL and the shared ground.

**`Permission denied` on GPIO, SPI or I2C.** Reboot after running `setup.sh` so your user's new groups take effect.

**Ash keeps recording or cuts you off.** Raise or lower `silence_threshold` in the settings. A noisy room needs a higher value.

**Gemini errors.** Check that the key in `.env` is right. If the configured model has been retired, Ash switches to another Flash model and prints which one it picked.

## Safety

The servos are strong enough to pinch. Keep fingers clear while it runs, and unplug the servo supply before changing the wiring.
