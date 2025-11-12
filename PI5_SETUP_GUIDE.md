# Raspberry Pi 5 LCD Setup Guide

## Problem Summary

The `goodtft/LCD-show` repository **does not work on Raspberry Pi 5** because it uses deprecated VideoCore APIs that don't exist on Pi 5. You'll see errors like:

```
fatal error: bcm_host.h: No such file or directory
Package 'libraspberrypi-dev' has no installation candidate
```

## Solution: Direct SPI Driver

We've created a direct SPI driver (`src/lcd_spi_driver.py`) that bypasses the old VideoCore APIs and communicates directly with the ILI9486 LCD controller via SPI.

## Setup Instructions

### Step 1: Enable SPI Interface

```bash
# On Raspberry Pi 5
sudo raspi-config
```

Navigate:
1. Interface Options
2. SPI
3. Enable
4. Finish
5. Reboot when prompted

### Step 2: Install Dependencies

```bash
# After reboot, SSH back in
cd ~/Ash
source venv/bin/activate  # if using venv

# Install required packages
pip install spidev RPi.GPIO numpy

# Or install all requirements
pip install -r requirements.txt
```

### Step 3: Verify SPI is Enabled

```bash
# Check if SPI devices exist
ls -l /dev/spi*

# Should show:
# /dev/spidev0.0
# /dev/spidev0.1

# Check if SPI module is loaded
lsmod | grep spi
# Should show: spi_bcm2835
```

### Step 4: Verify GPIO Pins

**Important:** The GPIO pin numbers in `lcd_spi_driver.py` are defaults. Your LCD model might use different pins.

Common pin mappings for 3.5" LCD:

| Function | Default GPIO | Alternative GPIO |
|----------|-------------|------------------|
| DC (Data/Command) | GPIO 25 | GPIO 24, GPIO 26 |
| RST (Reset) | GPIO 27 | GPIO 22, GPIO 23 |
| BL (Backlight) | GPIO 18 | GPIO 19, GPIO 13 |

**To find your LCD's pin mapping:**
1. Check your LCD's documentation
2. Check the LCD board for pin labels
3. Check the `goodtft/LCD-show` repository for your model's pinout

**To update pin mapping:**
Edit `src/lcd_spi_driver.py` and change the pin numbers in the `__init__` method:

```python
lcd = ILI9486SPI(
    width=480,
    height=320,
    dc_pin=25,    # Change if needed
    rst_pin=27,   # Change if needed
    bl_pin=18     # Change if needed
)
```

### Step 5: Test SPI Driver

```bash
# Test the SPI driver directly
python3 src/lcd_spi_driver.py
```

**Expected output:**
- LCD clears to black
- LCD clears to white
- Test patterns (red, green, blue)
- Face image (if available)

**If you see errors:**
- Check GPIO pin numbers match your LCD
- Check SPI is enabled: `lsmod | grep spi`
- Check SPI devices: `ls -l /dev/spi*`
- Check permissions: `groups` (should include `spi`)

### Step 6: Test Face Display

```bash
# Test face display (will automatically use SPI driver)
python3 src/face_display.py
```

**Expected output:**
- Face images cycle through all 7 expressions
- Each expression displays for 2 seconds
- Images are clear and properly sized (480×320)

## Troubleshooting

### Issue 1: Permission Denied on /dev/spi*

**Solution:**
```bash
# Add user to spi group
sudo usermod -a -G spi $USER

# Logout and login again, or:
newgrp spi

# Verify group membership
groups
# Should show: ... spi ...
```

### Issue 2: Display Shows Garbage or Nothing

**Possible causes:**
1. **Wrong GPIO pins:** Check your LCD's pin mapping
2. **Wrong SPI settings:** Try reducing SPI speed
3. **Incorrect initialization sequence:** Check ILI9486 datasheet

**Solutions:**
```bash
# Try reducing SPI speed in lcd_spi_driver.py
self.spi.max_speed_hz = 32000000  # Try 32 MHz instead of 64 MHz

# Check GPIO pins are correct
# Verify DC, RST, BL pins match your LCD

# Check connections are secure
# Re-seat the LCD on GPIO header
```

### Issue 3: SPI Not Working

**Check SPI is enabled:**
```bash
# Check SPI module
lsmod | grep spi
# Should show: spi_bcm2835

# Check SPI devices
ls -l /dev/spi*
# Should show: /dev/spidev0.0 and /dev/spidev0.1

# Check SPI configuration
cat /boot/config.txt | grep spi
# Should show: dtparam=spi=on
```

**If SPI is not enabled:**
```bash
# Enable SPI
sudo raspi-config
# Interface Options → SPI → Enable

# Reboot
sudo reboot
```

### Issue 4: Wrong Colors or Display Orientation

**Solution:**
```python
# In lcd_spi_driver.py, modify MADCTL register
# Different values for different orientations:

# 0x48 = Normal (portrait, BGR)
# 0x88 = Rotated 180° (portrait, BGR)
# 0x28 = Rotated 90° CCW (landscape, BGR)
# 0xE8 = Rotated 90° CW (landscape, BGR)

# Also check pixel format (RGB vs BGR)
# ILI9486 usually uses BGR order
```

### Issue 5: Display Too Slow or Flickers

**Solutions:**
```python
# Increase SPI speed (if stable)
self.spi.max_speed_hz = 64000000  # 64 MHz

# Reduce chunk size for more frequent updates
chunk_size = 2048  # Instead of 4096

# Optimize image conversion
# Use numpy operations instead of PIL operations
```

## Alternative: Device Tree Overlay

If your LCD model has a device tree overlay available, you can try using it:

```bash
# Check for device tree overlays
ls /boot/overlays/ | grep lcd
ls /boot/overlays/ | grep ili9486
ls /boot/overlays/ | grep spi

# Edit /boot/config.txt
sudo nano /boot/config.txt

# Add device tree overlay (example for ILI9486)
dtoverlay=spi1-1cs
dtoverlay=ili9486,rotate=90

# Reboot
sudo reboot
```

**Note:** Device tree overlays may not be available for all LCD models on Pi 5.

## Verification Checklist

After setup, verify:

- [ ] SPI is enabled: `lsmod | grep spi`
- [ ] SPI devices exist: `ls -l /dev/spi*`
- [ ] User is in spi group: `groups | grep spi`
- [ ] GPIO pins are correct for your LCD
- [ ] SPI driver test works: `python3 src/lcd_spi_driver.py`
- [ ] Face display works: `python3 src/face_display.py`
- [ ] All 7 expressions display correctly
- [ ] Images are clear and properly sized

## Next Steps

1. **Fine-tune GPIO pins** if needed for your LCD model
2. **Adjust display orientation** if needed
3. **Optimize performance** if display is slow
4. **Test with main application:** `python3 src/main.py --text`

## Resources

- ILI9486 Datasheet: Search for "ILI9486 datasheet"
- Raspberry Pi 5 GPIO: https://www.raspberrypi.com/documentation/computers/raspberry-pi.html
- SPI Documentation: https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#spi
- Direct SPI Driver: `src/lcd_spi_driver.py`
- Face Display Module: `src/face_display.py`

---

**Last Updated:** November 2025
**For:** Raspberry Pi 5 with 3.5" ILI9486 LCD Display

