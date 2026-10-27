# Ash on a Raspberry Pi

This is where Ash started: a physical robot with a 3.5" LCD face, two servo arms, a mic and a speaker. It uses the same brain as the web app (`ash/`), so only the "body" code lives here.

## Parts

- Raspberry Pi 5 (a Pi 4 works too)
- 3.5" ILI9486 SPI LCD, 480×320 (goodtft MPI3501 or Waveshare 3.5" A), plugged onto header pins 1–26
- PCA9685 servo board and two MG995 servos, with their own 5V supply (3A or more)
- USB microphone and a speaker

| PCA9685 | Raspberry Pi |
|---|---|
| VCC | Pin 1 (3.3V) |
| GND | Pin 6 (GND) |
| SDA | Pin 3 (GPIO 2) |
| SCL | Pin 5 (GPIO 3) |

Left arm on channel 0, right arm on channel 1. Never power the servos from the Pi's 5V pins, and connect the servo supply's ground to the Pi's ground.

## Running

```bash
./hardware/setup.sh            # installs everything and asks for your Groq key
sudo reboot
venv/bin/python -m hardware.main
```

Each part can be tested alone: `python -m hardware.lcd_spi_driver`, `hardware.face_display`, `hardware.gestures`, `hardware.audio_io`. Pins, servo limits and mic sensitivity are in `hardware/settings.yaml`.

If the screen stays white, set `register_width: 8` for a bare ILI9486 module, or lower `speed_hz` if the picture is garbled. If the servos don't move, `i2cdetect -y 1` should show `40`.
