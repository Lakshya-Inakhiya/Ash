"""
Direct SPI LCD Driver for Raspberry Pi 5
Compatible with 3.5" ILI9486 LCD displays

This driver bypasses the old VideoCore APIs and uses direct SPI communication.
Works on Raspberry Pi 5 where goodtft/LCD-show doesn't work.
"""

import time
import spidev
import RPi.GPIO as GPIO
from PIL import Image
import numpy as np


class ILI9486SPI:
    """
    Direct SPI driver for ILI9486 LCD controller.
    Compatible with 3.5" LCD displays on Raspberry Pi 5.
    """
    
    # ILI9486 Command Set
    CMD_NOP = 0x00
    CMD_SWRESET = 0x01
    CMD_SLPOUT = 0x11
    CMD_DISPON = 0x29
    CMD_CASET = 0x2A
    CMD_RASET = 0x2B
    CMD_RAMWR = 0x2C
    CMD_MADCTL = 0x36
    CMD_PIXFMT = 0x3A
    
    def __init__(self, width=480, height=320, spi_bus=0, spi_device=0, 
                 dc_pin=25, rst_pin=27, bl_pin=18):
        """
        Initialize ILI9486 LCD via SPI.
        
        Args:
            width: Display width in pixels (default: 480)
            height: Display height in pixels (default: 320)
            spi_bus: SPI bus number (default: 0)
            spi_device: SPI device number (default: 0)
            dc_pin: Data/Command pin (GPIO number)
            rst_pin: Reset pin (GPIO number)
            bl_pin: Backlight pin (GPIO number)
        """
        self.width = width
        self.height = height
        
        # GPIO pins (defaults for 3.5" LCD)
        self.dc_pin = dc_pin
        self.rst_pin = rst_pin
        self.bl_pin = bl_pin
        
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.dc_pin, GPIO.OUT)
        GPIO.setup(self.rst_pin, GPIO.OUT)
        GPIO.setup(self.bl_pin, GPIO.OUT)
        
        # Setup SPI
        self.spi = spidev.SpiDev()
        self.spi.open(spi_bus, spi_device)
        self.spi.max_speed_hz = 64000000  # 64 MHz
        self.spi.mode = 0b00
        
        # Initialize display
        self._init_display()
    
    def _write_command(self, cmd):
        """Write a command byte to the LCD."""
        GPIO.output(self.dc_pin, GPIO.LOW)  # Command mode
        self.spi.xfer2([cmd])
    
    def _write_data(self, data):
        """Write data bytes to the LCD."""
        GPIO.output(self.dc_pin, GPIO.HIGH)  # Data mode
        if isinstance(data, int):
            self.spi.xfer2([data])
        else:
            self.spi.xfer2(list(data))
    
    def _init_display(self):
        """Initialize the ILI9486 display."""
        # Reset display
        GPIO.output(self.rst_pin, GPIO.HIGH)
        time.sleep(0.01)
        GPIO.output(self.rst_pin, GPIO.LOW)
        time.sleep(0.01)
        GPIO.output(self.rst_pin, GPIO.HIGH)
        time.sleep(0.12)
        
        # Software reset
        self._write_command(self.CMD_SWRESET)
        time.sleep(0.12)
        
        # Exit sleep mode
        self._write_command(self.CMD_SLPOUT)
        time.sleep(0.12)
        
        # Set pixel format to 16-bit RGB565
        self._write_command(self.CMD_PIXFMT)
        self._write_data(0x55)  # 16-bit format
        
        # Set memory access control (MADCTL)
        self._write_command(self.CMD_MADCTL)
        self._write_data(0x48)  # BGR order, rotate 90 degrees
        
        # Display on
        self._write_command(self.CMD_DISPON)
        time.sleep(0.02)
        
        # Enable backlight
        GPIO.output(self.bl_pin, GPIO.HIGH)
    
    def set_window(self, x0, y0, x1, y1):
        """Set the display window for writing."""
        # Column address set
        self._write_command(self.CMD_CASET)
        self._write_data([x0 >> 8, x0 & 0xFF, x1 >> 8, x1 & 0xFF])
        
        # Row address set
        self._write_command(self.CMD_RASET)
        self._write_data([y0 >> 8, y0 & 0xFF, y1 >> 8, y1 & 0xFF])
        
        # Memory write
        self._write_command(self.CMD_RAMWR)
    
    def display_image(self, image):
        """
        Display a PIL Image on the LCD.
        
        Args:
            image: PIL Image object (will be resized to display size)
        """
        # Resize if needed
        if image.size != (self.width, self.height):
            image = image.resize((self.width, self.height), Image.Resampling.LANCZOS)
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Set full window
        self.set_window(0, 0, self.width - 1, self.height - 1)
        
        # Convert RGB to RGB565 and send to display
        rgb_array = np.array(image)
        
        # Convert RGB888 to RGB565
        r5 = (rgb_array[:, :, 0] >> 3).astype(np.uint16)
        g6 = (rgb_array[:, :, 1] >> 2).astype(np.uint16)
        b5 = (rgb_array[:, :, 2] >> 3).astype(np.uint16)
        rgb565 = (r5 << 11) | (g6 << 5) | b5
        
        # Convert to bytes (big-endian for ILI9486)
        pixel_data = rgb565.flatten()
        byte_data = pixel_data.astype('>u2').tobytes()  # Big-endian uint16
        
        # Send pixel data in chunks
        chunk_size = 4096  # Send in chunks to avoid buffer overflow
        GPIO.output(self.dc_pin, GPIO.HIGH)  # Data mode
        
        for i in range(0, len(byte_data), chunk_size):
            chunk = byte_data[i:i + chunk_size]
            # Convert to list for SPI
            data_list = list(chunk)
            self.spi.xfer2(data_list)
    
    def clear(self, color=(0, 0, 0)):
        """Clear the display with a solid color."""
        # Create a solid color image
        img = Image.new('RGB', (self.width, self.height), color)
        self.display_image(img)
    
    def close(self):
        """Clean up resources."""
        GPIO.output(self.bl_pin, GPIO.LOW)  # Turn off backlight
        self.spi.close()
        GPIO.cleanup()


def test_spi_lcd():
    """Test function for SPI LCD driver."""
    try:
        lcd = ILI9486SPI()
        print("LCD initialized successfully!")
        
        # Test 1: Clear to black
        print("Test 1: Clear to black...")
        lcd.clear((0, 0, 0))
        time.sleep(1)
        
        # Test 2: Clear to white
        print("Test 2: Clear to white...")
        lcd.clear((255, 255, 255))
        time.sleep(1)
        
        # Test 3: Display test pattern
        print("Test 3: Display test pattern...")
        img = Image.new('RGB', (480, 320), (255, 0, 0))  # Red
        lcd.display_image(img)
        time.sleep(1)
        
        img = Image.new('RGB', (480, 320), (0, 255, 0))  # Green
        lcd.display_image(img)
        time.sleep(1)
        
        img = Image.new('RGB', (480, 320), (0, 0, 255))  # Blue
        lcd.display_image(img)
        time.sleep(1)
        
        # Test 4: Display face image if available
        try:
            face_path = Path(__file__).parent.parent / "assets" / "faces" / "happy.png"
            if face_path.exists():
                print("Test 4: Display face image...")
                face_img = Image.open(face_path)
                lcd.display_image(face_img)
                time.sleep(2)
        except Exception as e:
            print(f"Could not load face image: {e}")
        
        lcd.close()
        print("Test complete!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    from pathlib import Path
    test_spi_lcd()

