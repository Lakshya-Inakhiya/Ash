# Raspberry Pi 5 LCD Driver Fix

## Problem: `goodtft/LCD-show` Doesn't Work on Pi 5

The `goodtft/LCD-show` repository is **incompatible with Raspberry Pi 5** because:

1. It uses old VideoCore APIs (`bcm_host.h`, `libraspberrypi-dev`)
2. These APIs don't exist on Raspberry Pi 5
3. Pi 5 uses VideoCore VII with a different architecture
4. The `fbcp` program in LCD-show relies on deprecated libraries

### Error Messages You'll See:
```
fatal error: bcm_host.h: No such file or directory
Package 'libraspberrypi-dev' has no installation candidate
```

## Solution Options

### Option 1: Direct SPI Driver (Recommended)

Use a direct SPI driver that communicates with the ILI9486 LCD controller directly, bypassing the old VideoCore APIs.

**Advantages:**
- Works on Raspberry Pi 5
- No dependency on deprecated libraries
- Full control over display
- Fast and efficient

**Implementation:**
See `src/lcd_spi_driver.py` for a direct SPI driver implementation.

**Setup:**
1. Install required Python packages:
   ```bash
   pip install spidev RPi.GPIO numpy
   ```

2. Enable SPI interface:
   ```bash
   sudo raspi-config
   # Navigate: Interface Options → SPI → Enable
   ```

3. Test the driver:
   ```bash
   python3 src/lcd_spi_driver.py
   ```

4. Update `face_display.py` to use the SPI driver instead of framebuffer.

### Option 2: Use Standard Linux Framebuffer (If Available)

Some LCD displays may work with standard Linux framebuffer drivers if the kernel supports them.

**Check if framebuffer devices exist:**
```bash
ls -l /dev/fb*
```

**Check kernel modules:**
```bash
lsmod | grep fbtft
modinfo fbtft_device
```

**Load fbtft module (if available):**
```bash
sudo modprobe fbtft_device name=ili9486 speed=64000000 fps=60
```

**Check if /dev/fb1 appears:**
```bash
ls -l /dev/fb*
```

**Note:** This may not work for all 3.5" LCD displays on Pi 5, as kernel support varies.

### Option 3: Use Alternative LCD Display

Consider using an LCD display that has official Raspberry Pi 5 support:

- **Official Raspberry Pi Touchscreen** (7" or 10")
- **Waveshare displays** with Pi 5 compatible drivers
- **SPI displays** with direct driver support

### Option 4: Use HDMI Display (Temporary)

While fixing the LCD issue, you can use an HDMI display for development:

```bash
# Connect HDMI monitor
# Display should work automatically
# Update config to use /dev/fb0 instead of /dev/fb1
```

## Recommended Implementation: Direct SPI Driver

### Step 1: Install Dependencies

```bash
# On Raspberry Pi 5
sudo apt-get update
sudo apt-get install -y python3-pip python3-pil python3-numpy

# Install Python packages
pip install spidev RPi.GPIO

# Enable SPI
sudo raspi-config
# Navigate: Interface Options → SPI → Enable
# Reboot after enabling
```

### Step 2: Test SPI Driver

```bash
cd ~/Ash
python3 src/lcd_spi_driver.py
```

You should see:
- LCD clears to black
- LCD clears to white
- Test patterns (red, green, blue)
- Face image (if available)

### Step 3: Update Face Display Module

Modify `src/face_display.py` to use the SPI driver when framebuffer is not available:

```python
# In face_display.py __init__:
if not self.has_framebuffer:
    try:
        from lcd_spi_driver import ILI9486SPI
        self.spi_driver = ILI9486SPI(
            width=self.width,
            height=self.height
        )
        self.use_spi = True
        print("Using direct SPI driver for LCD")
    except Exception as e:
        print(f"SPI driver not available: {e}")
        self.use_spi = False
        self._init_pygame_window()
```

### Step 4: Update Display Methods

Modify `_write_to_framebuffer` to use SPI when available:

```python
def _write_to_framebuffer(self, img):
    """Write an image to the framebuffer or SPI LCD."""
    if hasattr(self, 'use_spi') and self.use_spi:
        self.spi_driver.display_image(img)
    else:
        # Original framebuffer code
        raw_data = img.tobytes()
        with open(self.fb_path, 'wb') as fb:
            fb.write(raw_data)
```

## GPIO Pin Mapping for 3.5" LCD

The 3.5" LCD uses these GPIO pins (verify with your LCD model):

| LCD Pin | GPIO Pin | Function |
|---------|----------|----------|
| DC      | GPIO 25  | Data/Command |
| RST     | GPIO 27  | Reset |
| BL      | GPIO 18  | Backlight |
| MOSI    | GPIO 10  | SPI Data |
| SCLK    | GPIO 11  | SPI Clock |
| CS      | GPIO 8   | Chip Select |

**Note:** Verify these pins match your specific LCD model. Some LCDs use different pins.

## Troubleshooting

### SPI Not Working

**Check SPI is enabled:**
```bash
lsmod | grep spi
# Should show: spi_bcm2835
```

**Check SPI devices:**
```bash
ls -l /dev/spi*
# Should show: /dev/spidev0.0 and /dev/spidev0.1
```

**Test SPI communication:**
```bash
# Install spidev test tools
sudo apt-get install python3-spidev
python3 -c "import spidev; print('SPI available')"
```

### Display Shows Garbage

**Check GPIO pins:**
- Verify DC, RST, BL pins are correct
- Check connections are secure
- Test with multimeter if possible

**Check SPI speed:**
- Try reducing SPI speed: `self.spi.max_speed_hz = 32000000`
- Some LCDs need slower speeds

**Check initialization sequence:**
- Verify reset timing
- Check command sequence matches ILI9486 datasheet

### Permission Denied

**Add user to SPI group:**
```bash
sudo usermod -a -G spi $USER
# Logout and login again
```

**Check permissions:**
```bash
ls -l /dev/spi*
# Should show: crw-rw---- 1 root spi
```

## Alternative: Check for Pi 5 Compatible Driver

Search for updated drivers that support Raspberry Pi 5:

```bash
# Check if there's an updated LCD-show fork
git clone https://github.com/goodtft/LCD-show.git
cd LCD-show
# Check for Pi 5 branch or commits
git log --all --grep="pi5\|pi 5\|raspberry pi 5"
```

## Next Steps

1. **Try Option 1 (Direct SPI Driver):** Most reliable for Pi 5
2. **If that doesn't work:** Check if your LCD model has Pi 5 specific drivers
3. **As last resort:** Use HDMI display for development, or consider different LCD

## Resources

- ILI9486 Datasheet: Search for "ILI9486 datasheet"
- Raspberry Pi 5 GPIO: https://www.raspberrypi.com/documentation/computers/raspberry-pi.html
- SPI Documentation: https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#spi
- Direct SPI Driver: See `src/lcd_spi_driver.py`

---

**Last Updated:** November 2025
**For:** Raspberry Pi 5 with 3.5" ILI9486 LCD Display

