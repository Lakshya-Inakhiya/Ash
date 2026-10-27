"""Shows Ash's face: on the SPI LCD on a Pi, or in a pygame window elsewhere."""

import time
from pathlib import Path

import pygame
from PIL import Image

from utils import PROJECT_ROOT

EXPRESSIONS = ["happy", "sad", "neutral", "listening", "speaking", "thinking", "error"]


class FaceDisplay:
    def __init__(self, config):
        cfg = config["display"]
        self.size = (cfg["resolution"]["width"], cfg["resolution"]["height"])
        self.lcd = None
        self.screen = None
        self.current_expression = None

        if Path("/proc/device-tree/model").exists():
            try:
                from lcd_spi_driver import ILI9486SPI
                self.lcd = ILI9486SPI(*self.size, **cfg.get("spi", {}))
                print("LCD ready (SPI)")
            except Exception as e:
                print(f"LCD not available ({e}); using a window instead.")
        if self.lcd is None:
            try:
                pygame.display.init()
                self.screen = pygame.display.set_mode(self.size)
                pygame.display.set_caption("Ash")
            except pygame.error as e:
                print(f"No display available ({e}); faces will only be logged.")

        faces_dir = PROJECT_ROOT / cfg["faces_directory"]
        self.faces = {}
        for name in EXPRESSIONS:
            path = faces_dir / f"{name}.png"
            if path.exists():
                self.faces[name] = Image.open(path).convert("RGB").resize(self.size, Image.Resampling.LANCZOS)
            else:
                print(f"Missing face image: {path}")

    def set_expression(self, name):
        img = self.faces.get(name)
        if img is None:
            return False
        if not (self.lcd or self.screen):
            print(f"[FACE] {name}")
        try:
            self._show(img)
        except Exception as e:
            print(f"Display error: {e}")
            return False
        self.current_expression = name
        return True

    def _show(self, img):
        if self.lcd:
            self.lcd.display_image(img)
        elif self.screen:
            self.screen.blit(pygame.image.frombytes(img.tobytes(), img.size, "RGB"), (0, 0))
            pygame.display.flip()
            pygame.event.pump()

    def clear(self):
        self._show(Image.new("RGB", self.size))
        self.current_expression = None

    def close(self):
        self.clear()
        if self.lcd:
            self.lcd.close()
        if self.screen:
            pygame.display.quit()


if __name__ == "__main__":
    from utils import load_config

    display = FaceDisplay(load_config())
    for name in display.faces:
        print(name)
        display.set_expression(name)
        time.sleep(1.5)
    display.close()
