"""
Direct SPI LCD Driver for Raspberry Pi 5
Compatible with 3.5" ILI9486 LCD displays

This driver bypasses the old VideoCore APIs and uses direct SPI communication.
Works on Raspberry Pi 5 where goodtft/LCD-show doesn't work.
"""

import time
import spidev
try:
    import gpiod
    GPIO_AVAILABLE = True
    USE_GPIOD = True
    # Verify gpiod can actually be used
    try:
        # Test if we can list chips
        import os
        test_chips = [f for f in os.listdir('/dev') if f.startswith('gpiochip')]
    except:
        pass
except ImportError:
    # Fallback for older Pi models (though this driver is for Pi 5)
    try:
        import RPi.GPIO as GPIO
        GPIO_AVAILABLE = True
        USE_GPIOD = False
    except ImportError:
        GPIO_AVAILABLE = False
        USE_GPIOD = False
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
                 dc_pin=24, rst_pin=25, bl_pin=18, speed_hz=32000000, rotation=1):
        """
        Initialize ILI9486 LCD via SPI.
        
        Args:
            width: Display width in pixels (default: 480)
            height: Display height in pixels (default: 320)
            spi_bus: SPI bus number (default: 0)
            spi_device: SPI device number (default: 0)
            dc_pin: Data/Command pin (GPIO number, default: 24)
            rst_pin: Reset pin (GPIO number, default: 25)
            bl_pin: Backlight pin (GPIO number, default: 18)
            speed_hz: SPI speed in Hz (default: 32000000 = 32 MHz)
            rotation: Display rotation (0-3, default: 1 = 90 degrees)
        """
        self.width = width
        self.height = height
        self.rotation = rotation
        
        # GPIO pins (defaults match old code: DC=24, RST=25)
        self.dc_pin = dc_pin
        self.rst_pin = rst_pin
        self.bl_pin = bl_pin
        
        # Setup GPIO using gpiod (for Raspberry Pi 5)
        if GPIO_AVAILABLE and USE_GPIOD:
            # On Pi 5, GPIO chip is usually gpiochip4, but auto-detect if needed
            chip_found = False
            last_error = None
            
            # First, try common chip names
            for chip_name in ['gpiochip4', 'gpiochip0']:
                try:
                    self.chip = gpiod.Chip(chip_name, gpiod.Chip.OPEN_BY_NAME)
                    chip_found = True
                    break
                except Exception as e:
                    last_error = e
                    continue
            
            # If not found, try to find any available GPIO chip
            if not chip_found:
                try:
                    import os
                    gpio_chips = [f for f in os.listdir('/dev') if f.startswith('gpiochip')]
                    if gpio_chips:
                        # Sort and try each one (try by path first, then by name)
                        gpio_chips.sort()
                        for chip_name in gpio_chips:
                            # Try opening by path
                            try:
                                chip_path = f'/dev/{chip_name}'
                                self.chip = gpiod.Chip(chip_path, gpiod.Chip.OPEN_BY_PATH)
                                chip_found = True
                                break
                            except Exception as e1:
                                # Try opening by name
                                try:
                                    self.chip = gpiod.Chip(chip_name, gpiod.Chip.OPEN_BY_NAME)
                                    chip_found = True
                                    break
                                except Exception as e2:
                                    last_error = e2 if last_error is None else last_error
                                    continue
                except Exception as e:
                    last_error = e
            
            if not chip_found:
                import os
                error_msg = "Failed to open GPIO chip."
                if last_error:
                    error_msg += f" Last error: {last_error}"
                
                # Add diagnostic information
                try:
                    gpio_chips = [f for f in os.listdir('/dev') if f.startswith('gpiochip')]
                    if gpio_chips:
                        error_msg += f"\nFound GPIO chips: {', '.join(gpio_chips)}"
                        # Check permissions
                        for chip in gpio_chips:
                            chip_path = f'/dev/{chip}'
                            if os.path.exists(chip_path):
                                stat_info = os.stat(chip_path)
                                error_msg += f"\n  {chip_path}: mode {oct(stat_info.st_mode)[-3:]}, uid={stat_info.st_uid}, gid={stat_info.st_gid}"
                    else:
                        error_msg += "\nNo GPIO chips found in /dev/"
                except Exception as e:
                    error_msg += f"\nCould not check /dev/: {e}"
                
                error_msg += "\n\nTroubleshooting:"
                error_msg += "\n1. Add user to gpio group: sudo usermod -a -G gpio $USER (then logout/login)"
                error_msg += "\n2. Or fix permissions: sudo chmod 666 /dev/gpiochip*"
                error_msg += "\n3. Verify gpiod: python3 -c 'import gpiod; print(gpiod.__version__)'"
                error_msg += "\n4. Check if system gpiod conflicts with pip: pip uninstall gpiod (system package should be enough)"
                raise RuntimeError(error_msg)
            
            # Request GPIO lines as outputs
            self.dc_line = self.chip.get_line(self.dc_pin)
            self.rst_line = self.chip.get_line(self.rst_pin)
            self.bl_line = self.chip.get_line(self.bl_pin)
            
            self.dc_line.request(consumer='lcd_dc', type=gpiod.LINE_REQ_DIR_OUT)
            self.rst_line.request(consumer='lcd_rst', type=gpiod.LINE_REQ_DIR_OUT)
            self.bl_line.request(consumer='lcd_bl', type=gpiod.LINE_REQ_DIR_OUT)
        elif GPIO_AVAILABLE and not USE_GPIOD:
            # Fallback to RPi.GPIO for older Pi models
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            GPIO.setup(self.dc_pin, GPIO.OUT)
            GPIO.setup(self.rst_pin, GPIO.OUT)
            GPIO.setup(self.bl_pin, GPIO.OUT)
            self.chip = None
        else:
            raise RuntimeError("No GPIO library available. Install gpiod or RPi.GPIO.")
        
        # Setup SPI
        self.spi = spidev.SpiDev()
        self.spi.open(spi_bus, spi_device)
        self.spi.max_speed_hz = speed_hz
        self.spi.mode = 0b00
        
        # Initialize display
        self._init_display()
    
    def _set_dc(self, value):
        """Set DC pin (Data/Command) - LOW for command, HIGH for data."""
        if GPIO_AVAILABLE and USE_GPIOD:
            self.dc_line.set_value(value)
        else:
            GPIO.output(self.dc_pin, GPIO.LOW if value == 0 else GPIO.HIGH)
    
    def _set_rst(self, value):
        """Set RST pin - HIGH for normal operation, LOW for reset."""
        if GPIO_AVAILABLE and USE_GPIOD:
            self.rst_line.set_value(value)
        else:
            GPIO.output(self.rst_pin, GPIO.LOW if value == 0 else GPIO.HIGH)
    
    def _set_bl(self, value):
        """Set BL pin (Backlight) - HIGH to enable, LOW to disable."""
        if GPIO_AVAILABLE and USE_GPIOD:
            self.bl_line.set_value(value)
        else:
            GPIO.output(self.bl_pin, GPIO.LOW if value == 0 else GPIO.HIGH)
    
    def _write_command(self, cmd):
        """Write a command byte to the LCD."""
        self._set_dc(0)  # Command mode
        self.spi.xfer2([cmd])
    
    def _write_data(self, data):
        """Write data bytes to the LCD."""
        self._set_dc(1)  # Data mode
        if isinstance(data, int):
            self.spi.xfer2([data])
        else:
            self.spi.xfer2(list(data))
    
    def _init_display(self):
        """Initialize the ILI9486 display."""
        # Reset display
        self._set_rst(1)
        time.sleep(0.01)
        self._set_rst(0)
        time.sleep(0.01)
        self._set_rst(1)
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
        
        # Set memory access control (MADCTL) based on rotation
        # MADCTL bits: MY(7) MX(6) MV(5) ML(4) BGR(3) MH(2) - (0-1 unused)
        # Rotation values:
        #   0: Normal (0x08 = BGR)
        #   1: 90° clockwise (0x28 = BGR + MY + MV)
        #   2: 180° (0xC8 = BGR + MY + MX)
        #   3: 270° clockwise (0xE8 = BGR + MY + MX + MV)
        rotation_madctl = {
            0: 0x08,  # Normal, BGR
            1: 0x28,  # 90° clockwise, BGR + MY + MV
            2: 0xC8,  # 180°, BGR + MY + MX
            3: 0xE8,  # 270° clockwise, BGR + MY + MX + MV
        }
        madctl_value = rotation_madctl.get(self.rotation, 0x28)  # Default to rotation 1
        
        self._write_command(self.CMD_MADCTL)
        self._write_data(madctl_value)
        
        # Display on
        self._write_command(self.CMD_DISPON)
        time.sleep(0.02)
        
        # Enable backlight
        self._set_bl(1)
    
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
        self._set_dc(1)  # Data mode
        
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
        self._set_bl(0)  # Turn off backlight
        self.spi.close()
        if GPIO_AVAILABLE and USE_GPIOD:
            # Release GPIO lines
            if hasattr(self, 'dc_line'):
                self.dc_line.release()
            if hasattr(self, 'rst_line'):
                self.rst_line.release()
            if hasattr(self, 'bl_line'):
                self.bl_line.release()
            if hasattr(self, 'chip'):
                self.chip.close()
        else:
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

