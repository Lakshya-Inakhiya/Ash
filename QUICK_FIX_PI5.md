# Quick Fix for Raspberry Pi 5 LCD Issue

## Problem

You're seeing this error on Raspberry Pi 5:
```
fatal error: bcm_host.h: No such file or directory
Package 'libraspberrypi-dev' has no installation candidate
```

**The `goodtft/LCD-show` repository does NOT work on Raspberry Pi 5!**

## Quick Solution

### Step 1: Enable SPI

```bash
sudo raspi-config
# Navigate: Interface Options → SPI → Enable
# Reboot after enabling
sudo reboot
```

### Step 2: Install SPI Driver Dependencies

```bash
# After reboot, SSH back in
cd ~/Ash
source venv/bin/activate  # if using venv

# Install required packages
pip install spidev RPi.GPIO

# Or install all requirements
pip install -r requirements.txt
```

### Step 3: Verify SPI is Enabled

```bash
# Check SPI devices
ls -l /dev/spi*
# Should show: /dev/spidev0.0 and /dev/spidev0.1

# Check SPI module
lsmod | grep spi
# Should show: spi_bcm2835
```

### Step 4: Test SPI Driver

```bash
# Test the SPI driver
python3 src/lcd_spi_driver.py
```

**Expected:** LCD should show test patterns (black, white, red, green, blue, face image)

**If it doesn't work:** Check GPIO pins in `src/lcd_spi_driver.py` - they might not match your LCD model.

### Step 5: Test Face Display

```bash
# Test face display (will automatically use SPI driver)
python3 src/face_display.py
```

**Expected:** Face images should cycle through all 7 expressions on the LCD.

## Important Notes

### GPIO Pins

The SPI driver uses these default GPIO pins:
- **DC (Data/Command):** GPIO 25
- **RST (Reset):** GPIO 27
- **BL (Backlight):** GPIO 18

**Your LCD might use different pins!** Check your LCD's documentation or the LCD board for pin labels.

**To change pins:** Edit `src/lcd_spi_driver.py` and modify the `__init__` method:

```python
lcd = ILI9486SPI(
    width=480,
    height=320,
    dc_pin=25,    # Change if needed
    rst_pin=27,   # Change if needed
    bl_pin=18     # Change if needed
)
```

### Common Pin Mappings for 3.5" LCD

| Function | Common GPIO Pins |
|----------|------------------|
| DC | GPIO 25, GPIO 24, GPIO 26 |
| RST | GPIO 27, GPIO 22, GPIO 23 |
| BL | GPIO 18, GPIO 19, GPIO 13 |

## Troubleshooting

### Permission Denied on /dev/spi*

```bash
# Add user to spi group
sudo usermod -a -G spi $USER

# Logout and login again, or:
newgrp spi

# Verify
groups
# Should show: ... spi ...
```

### Display Shows Nothing or Garbage

1. **Check GPIO pins** match your LCD
2. **Check connections** are secure
3. **Try reducing SPI speed** in `lcd_spi_driver.py`:
   ```python
   self.spi.max_speed_hz = 32000000  # Try 32 MHz instead of 64 MHz
   ```

### SPI Not Working

```bash
# Check SPI is enabled
cat /boot/config.txt | grep spi
# Should show: dtparam=spi=on

# If not enabled:
sudo raspi-config
# Interface Options → SPI → Enable
sudo reboot
```

## Full Documentation

For more details, see:
- `PI5_LCD_FIX.md` - Detailed explanation of Pi 5 incompatibility
- `PI5_SETUP_GUIDE.md` - Complete setup guide
- `LCD_TROUBLESHOOTING.md` - General troubleshooting guide

## Next Steps

1. ✅ Enable SPI
2. ✅ Install dependencies
3. ✅ Test SPI driver
4. ✅ Verify GPIO pins match your LCD
5. ✅ Test face display
6. ✅ Test with main application: `python3 src/main.py --text`

---

**Last Updated:** November 2025
**For:** Raspberry Pi 5 with 3.5" ILI9486 LCD Display

