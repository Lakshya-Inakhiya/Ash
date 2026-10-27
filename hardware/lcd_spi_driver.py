"""SPI driver for 3.5" ILI9486 LCDs (goodtft MPI3501 / Waveshare 3.5" A).

Talks to the panel directly over SPI, so it works on the Pi 5 where the
old LCD-show framebuffer driver doesn't. Uses libgpiod v2 for the control pins.
"""

import time
from pathlib import Path

import gpiod
import numpy as np
import spidev
from gpiod.line import Direction, Value
from PIL import Image

# MADCTL values per rotation (BGR bit set). 1 = landscape, matching LCD-show's "rotate 90".
MADCTL = {0: 0x08, 1: 0x28, 2: 0xC8, 3: 0xE8}

# Init sequence from the kernel's waveshare35a overlay (same panel as the MPI3501).
INIT_SEQUENCE = [
    (0xB0, [0x00]),
    (0x11, None), ("sleep", 0.25),
    (0x3A, [0x55]),                     # 16-bit RGB565
    (0xC2, [0x44]),
    (0xC5, [0x00, 0x00, 0x00, 0x00]),
    (0xE0, [0x0F, 0x1F, 0x1C, 0x0C, 0x0F, 0x08, 0x48, 0x98, 0x37, 0x0A, 0x13, 0x04, 0x11, 0x0D, 0x00]),
    (0xE1, [0x0F, 0x32, 0x2E, 0x0B, 0x0D, 0x05, 0x47, 0x75, 0x37, 0x06, 0x10, 0x03, 0x24, 0x20, 0x00]),
    (0xE2, [0x0F, 0x32, 0x2E, 0x0B, 0x0D, 0x05, 0x47, 0x75, 0x37, 0x06, 0x10, 0x03, 0x24, 0x20, 0x00]),
    (0x11, None), ("sleep", 0.12),
    (0x29, None),                       # display on
]


def find_gpio_chip():
    """Find the chip that drives the 40-pin header (RP1 on Pi 5, BCM on older Pis)."""
    chips = sorted(Path("/dev").glob("gpiochip*"))
    for path in chips:
        with gpiod.Chip(str(path)) as chip:
            label = chip.get_info().label
        if "rp1" in label or "bcm2" in label:
            return str(path)
    if chips:
        return str(chips[0])
    raise RuntimeError("No /dev/gpiochip* found. Is this a Raspberry Pi?")


class ILI9486SPI:
    def __init__(self, width=480, height=320, bus=0, device=0, dc_pin=24,
                 rst_pin=25, bl_pin=18, speed_hz=16_000_000, rotation=1, register_width=16):
        """register_width: 16 for MPI3501/Waveshare boards (they have a 16-bit
        shift register in front of the controller), 8 for bare ILI9486 modules."""
        self.width, self.height = width, height
        self.rotation = rotation
        self.register_width = register_width
        self.dc, self.rst, self.bl = dc_pin, rst_pin, bl_pin

        self.gpio = gpiod.request_lines(
            find_gpio_chip(),
            consumer="ash-lcd",
            config={(dc_pin, rst_pin, bl_pin): gpiod.LineSettings(direction=Direction.OUTPUT)},
        )
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        self.spi.max_speed_hz = speed_hz
        self.spi.mode = 0
        self._init_display()

    def _pin(self, pin, on):
        self.gpio.set_value(pin, Value.ACTIVE if on else Value.INACTIVE)

    def _send(self, values):
        if self.register_width == 16:
            values = [b for v in values for b in (0x00, v)]
        self.spi.writebytes2(bytes(values))

    def command(self, cmd, params=None):
        self._pin(self.dc, False)
        self._send([cmd])
        if params:
            self._pin(self.dc, True)
            self._send(params)

    def _init_display(self):
        for on, delay in ((True, 0.01), (False, 0.01), (True, 0.12)):
            self._pin(self.rst, on)
            time.sleep(delay)
        for cmd, arg in INIT_SEQUENCE:
            if cmd == "sleep":
                time.sleep(arg)
            else:
                self.command(cmd, arg)
        self.command(0x36, [MADCTL.get(self.rotation, 0x28)])
        self._pin(self.bl, True)

    def display_image(self, image):
        if image.size != (self.width, self.height):
            image = image.resize((self.width, self.height), Image.Resampling.LANCZOS)
        rgb = np.asarray(image.convert("RGB"), dtype=np.uint16)
        rgb565 = ((rgb[..., 0] >> 3) << 11) | ((rgb[..., 1] >> 2) << 5) | (rgb[..., 2] >> 3)

        w, h = self.width - 1, self.height - 1
        self.command(0x2A, [0, 0, w >> 8, w & 0xFF])
        self.command(0x2B, [0, 0, h >> 8, h & 0xFF])
        self.command(0x2C)
        self._pin(self.dc, True)
        self.spi.writebytes2(rgb565.astype(">u2").tobytes())

    def clear(self, color=(0, 0, 0)):
        self.display_image(Image.new("RGB", (self.width, self.height), color))

    def close(self):
        self._pin(self.bl, False)
        self.spi.close()
        self.gpio.release()


if __name__ == "__main__":
    lcd = ILI9486SPI()
    for color in [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 255)]:
        print(f"Showing {color}")
        lcd.clear(color)
        time.sleep(1)
    lcd.close()
