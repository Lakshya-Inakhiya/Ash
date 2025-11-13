"""
Face Display Module for Ash Robot.

This module handles rendering facial expressions on the 3.5" LCD display
using PIL/Pillow and the framebuffer device created by the LCD-show driver.

The display expects user-provided PNG images (480x320) for each expression.
"""

import os
from pathlib import Path
from PIL import Image
import time
import pygame


class FaceDisplay:
    """
    Manages facial expressions on the LCD display.
    
    This class loads PNG images from the assets/faces directory and displays
    them on the framebuffer device (/dev/fb1) created by the LCD-show driver.
    """
    
    # Available expressions
    EXPRESSIONS = [
        "happy", "sad", "neutral", "listening", 
        "speaking", "thinking", "error"
    ]
    
    def __init__(self, config):
        """
        Initialize the face display.
        
        Args:
            config: Configuration dictionary with display settings
        """
        self.config = config
        self.fb_path = config['display']['framebuffer_path']
        self.width = config['display']['resolution']['width']
        self.height = config['display']['resolution']['height']
        
        # Get the project root and faces directory
        project_root = Path(__file__).parent.parent
        faces_dir = config['display']['faces_directory']
        self.faces_path = project_root / faces_dir
        
        # Cache for loaded images
        self.image_cache = {}
        
        # Current expression
        self.current_expression = None
        
        # Check if running on Pi with framebuffer
        self.has_framebuffer = os.path.exists(self.fb_path)
        
        # SPI driver for Pi 5 (when framebuffer not available)
        self.spi_driver = None
        self.use_spi = False
        
        # Pygame window for simulation mode
        self.window = None
        self.screen = None
        
        # Try to initialize display backend (in order of preference)
        if self.has_framebuffer:
            print(f"Framebuffer detected: {self.fb_path}")
        else:
            print(f"Warning: Framebuffer {self.fb_path} not found.")
            # Try SPI driver (for Pi 5)
            try:
                # Only try SPI on Raspberry Pi (not on Mac)
                if os.path.exists('/proc/device-tree/model'):
                    from lcd_spi_driver import ILI9486SPI
                    
                    # Get SPI configuration from settings
                    spi_config = config.get('display', {}).get('spi', {})
                    self.spi_driver = ILI9486SPI(
                        width=self.width,
                        height=self.height,
                        spi_bus=spi_config.get('bus', 0),
                        spi_device=spi_config.get('device', 0),
                        dc_pin=spi_config.get('dc_pin', 24),
                        rst_pin=spi_config.get('rst_pin', 25),
                        bl_pin=spi_config.get('bl_pin', 18),
                        speed_hz=spi_config.get('speed_hz', 32000000),
                        rotation=spi_config.get('rotation', 1)
                    )
                    self.use_spi = True
                    print(f"Using direct SPI driver for LCD (Pi 5 compatible)")
                    print(f"  SPI: bus={spi_config.get('bus', 0)}, device={spi_config.get('device', 0)}")
                    print(f"  Pins: DC={spi_config.get('dc_pin', 24)}, RST={spi_config.get('rst_pin', 25)}, BL={spi_config.get('bl_pin', 18)}")
                    print(f"  Speed: {spi_config.get('speed_hz', 32000000) // 1000000} MHz, Rotation: {spi_config.get('rotation', 1)}")
                else:
                    raise ImportError("Not running on Raspberry Pi")
            except Exception as e:
                print(f"SPI driver not available: {e}")
                print("Face display will run in simulation mode with pygame window.")
                print("This is normal when developing on Mac. Deploy to Pi for actual display.")
                self._init_pygame_window()
        
        # Load all face images into cache
        self._load_images()
    
    def _init_pygame_window(self):
        """
        Initialize pygame window for simulation mode (Mac development).
        """
        try:
            pygame.init()
            self.screen = pygame.display.set_mode((self.width, self.height))
            pygame.display.set_caption("Ash Robot - Face Display Simulator")
            print("Pygame window initialized for face display simulation")
        except Exception as e:
            print(f"Warning: Could not initialize pygame window: {e}")
            self.screen = None
    
    def _load_images(self):
        """
        Load all face PNG images into memory cache.
        
        This speeds up expression switching by avoiding disk I/O during runtime.
        """
        if not self.faces_path.exists():
            print(f"Warning: Faces directory not found at {self.faces_path}")
            print("Please create the directory and add PNG files for each expression:")
            for expr in self.EXPRESSIONS:
                print(f"  - {expr}.png")
            return
        
        for expression in self.EXPRESSIONS:
            image_path = self.faces_path / f"{expression}.png"
            
            if image_path.exists():
                try:
                    # Load and resize if needed
                    img = Image.open(image_path)
                    
                    # Ensure correct size
                    if img.size != (self.width, self.height):
                        print(f"Resizing {expression}.png from {img.size} to {self.width}x{self.height}")
                        img = img.resize((self.width, self.height), Image.Resampling.LANCZOS)
                    
                    # Convert to RGB (framebuffer expects RGB)
                    img = img.convert('RGB')
                    
                    # Cache the image
                    self.image_cache[expression] = img
                    print(f"Loaded face: {expression}")
                    
                except Exception as e:
                    print(f"Error loading {expression}.png: {e}")
            else:
                print(f"Warning: Missing face image: {image_path}")
    
    def set_expression(self, expression):
        """
        Display a facial expression on the LCD.
        
        Args:
            expression: Name of the expression (e.g., "happy", "sad")
        
        Returns:
            bool: True if successful, False otherwise
        """
        if expression not in self.EXPRESSIONS:
            print(f"Warning: Unknown expression '{expression}'. Available: {self.EXPRESSIONS}")
            return False
        
        if expression not in self.image_cache:
            print(f"Warning: Expression '{expression}' not loaded. Image file may be missing.")
            return False
        
        # Get the cached image
        img = self.image_cache[expression]
        
        # Display on framebuffer if available
        if self.has_framebuffer:
            try:
                self._write_to_framebuffer(img)
                self.current_expression = expression
                return True
            except Exception as e:
                print(f"Error writing to framebuffer: {e}")
                return False
        elif self.use_spi and self.spi_driver:
            # Use SPI driver (for Pi 5)
            try:
                self.spi_driver.display_image(img)
                self.current_expression = expression
                return True
            except Exception as e:
                print(f"Error displaying on SPI LCD: {e}")
                return False
        else:
            # Simulation mode (for development on Mac) - show in pygame window
            try:
                self._display_in_window(img)
                print(f"[DISPLAY] Expression: {expression}")
                self.current_expression = expression
                return True
            except Exception as e:
                print(f"Error displaying in window: {e}")
                print(f"[DISPLAY] Expression: {expression} (window failed)")
                self.current_expression = expression
                return True
    
    def _display_in_window(self, img):
        """
        Display an image in the pygame window (simulation mode).
        
        Args:
            img: PIL Image object (RGB mode, correct size)
        """
        if self.screen is None:
            return
        
        # Convert PIL image to pygame surface
        img_str = img.tobytes()
        pygame_img = pygame.image.fromstring(img_str, img.size, 'RGB')
        
        # Display on screen
        self.screen.blit(pygame_img, (0, 0))
        pygame.display.flip()
        
        # Process pygame events to keep window responsive
        pygame.event.pump()
    
    def _write_to_framebuffer(self, img):
        """
        Write an image to the framebuffer device.
        
        Args:
            img: PIL Image object (RGB mode, correct size)
        """
        # Convert image to raw RGB bytes
        # The framebuffer expects raw pixel data
        raw_data = img.tobytes()
        
        # Write to framebuffer
        with open(self.fb_path, 'wb') as fb:
            fb.write(raw_data)
    
    def clear(self):
        """
        Clear the display (show black screen).
        """
        if self.has_framebuffer:
            try:
                # Create a black image
                black_img = Image.new('RGB', (self.width, self.height), (0, 0, 0))
                self._write_to_framebuffer(black_img)
                self.current_expression = None
            except Exception as e:
                print(f"Error clearing display: {e}")
        elif self.use_spi and self.spi_driver:
            try:
                self.spi_driver.clear((0, 0, 0))
                self.current_expression = None
            except Exception as e:
                print(f"Error clearing SPI display: {e}")
        else:
            # Clear pygame window
            if self.screen:
                self.screen.fill((0, 0, 0))
                pygame.display.flip()
            print("[DISPLAY] Cleared")
            self.current_expression = None
    
    def test_all_expressions(self, delay=2):
        """
        Test function to cycle through all expressions.
        Useful for verifying all face images are loaded correctly.
        
        Args:
            delay: Seconds to display each expression
        """
        print("Testing all expressions...")
        for expression in self.EXPRESSIONS:
            if expression in self.image_cache:
                print(f"Displaying: {expression}")
                self.set_expression(expression)
                time.sleep(delay)
        print("Test complete!")
    
    def get_current_expression(self):
        """
        Get the currently displayed expression.
        
        Returns:
            str: Current expression name, or None if no expression is displayed
        """
        return self.current_expression
    
    def close(self):
        """
        Clean up resources.
        """
        self.clear()
        self.image_cache.clear()
        
        # Close SPI driver if it was initialized
        if self.spi_driver is not None:
            try:
                self.spi_driver.close()
            except Exception as e:
                print(f"Error closing SPI driver: {e}")
        
        # Quit pygame if it was initialized
        if self.screen is not None:
            pygame.quit()


def main():
    """
    Test function for the face display module.
    Run this directly to test the display functionality.
    """
    import sys
    sys.path.append(str(Path(__file__).parent))
    from utils import load_config
    
    print("Face Display Test")
    print("-" * 40)
    
    try:
        config = load_config()
        display = FaceDisplay(config)
        
        print(f"\nFramebuffer: {display.fb_path}")
        print(f"Resolution: {display.width}x{display.height}")
        print(f"Loaded expressions: {list(display.image_cache.keys())}")
        
        # Test all expressions
        if display.image_cache:
            display.test_all_expressions(delay=2)
        else:
            print("\nNo face images loaded. Please add PNG files to assets/faces/")
        
        display.close()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

