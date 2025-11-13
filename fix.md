# LCD Pin Fix - Complete Command Guide

This guide provides **all commands** needed to update your code from GitHub and fix the LCD pin configuration on Raspberry Pi 5.

## Prerequisites

- Raspberry Pi 5 with SSH access
- Project already cloned (or will clone in Step 1)
- LCD connected to Pi 5

---

## Step 1: Navigate to Project Directory

```bash
# If project is in home directory
cd ~/Ash-1

# OR if project is in Desktop
cd ~/Desktop/Ash-1

# OR if you need to clone fresh from GitHub
cd ~
git clone <your-repo-url> Ash-1
cd Ash-1
```

---

## Step 2: Pull Latest Code from GitHub

```bash
# Make sure you're in the project directory
cd ~/Ash-1

# Check current status
git status

# Pull latest changes from GitHub
git pull origin main

# OR if you need to fetch and merge
git fetch origin
git merge origin/main

# Verify you have the latest code
git log --oneline -5
```

**Expected:** You should see the latest commits including the LCD pin configuration updates.

---

## Step 3: Verify Configuration File Has Pin Settings

```bash
# Check that settings.yaml has SPI configuration
cat config/settings.yaml | grep -A 10 "spi:"

# Should show:
#   spi:
#     bus: 0
#     device: 0
#     dc_pin: 24
#     rst_pin: 25
#     bl_pin: 18
#     speed_hz: 32000000
#     rotation: 1
```

**If the SPI section is missing**, the code update didn't work. Check your git pull.

---

## Step 4: Activate Virtual Environment

```bash
# Navigate to project
cd ~/Ash-1

# Activate virtual environment
source venv/bin/activate

# OR use the activation script
source activate.sh

# Verify you're in venv (prompt should show "(ash)" or "(venv)")
which python3
# Should show: /home/pi/Ash-1/venv/bin/python3
```

---

## Step 5: Install/Update Required Dependencies

```bash
# Make sure venv is activated first!
source venv/bin/activate

# Install SPI and GPIO libraries (if not already installed)
pip install spidev RPi.GPIO

# OR install all requirements
pip install -r requirements.txt

# Verify installation
pip list | grep -E "spidev|RPi.GPIO"
# Should show both packages
```

---

## Step 6: Enable SPI Interface (if not already enabled)

```bash
# Check if SPI is already enabled
cat /boot/config.txt | grep spi

# If you see "dtparam=spi=on", SPI is enabled. Skip to Step 7.
# If not, enable it:

# Open raspi-config
sudo raspi-config

# Navigate:
# 1. Interface Options
# 2. SPI
# 3. Enable
# 4. Finish
# 5. Reboot when prompted

# After reboot, SSH back in and continue
```

---

## Step 7: Verify SPI is Working

```bash
# Check SPI devices exist
ls -l /dev/spi*

# Should show:
# /dev/spidev0.0
# /dev/spidev0.1

# Check SPI kernel module is loaded
lsmod | grep spi

# Should show: spi_bcm2835

# Check SPI is enabled in config
cat /boot/config.txt | grep spi
# Should show: dtparam=spi=on
```

**If SPI devices are missing**, you need to enable SPI (Step 6) and reboot.

---

## Step 8: Fix SPI Permissions (if needed)

```bash
# Check if you can access SPI devices
ls -l /dev/spi*

# If you see permission denied errors, add user to spi group:
sudo usermod -a -G spi $USER

# Logout and login again, OR:
newgrp spi

# Verify you're in spi group
groups
# Should show: ... spi ...

# Test access
ls -l /dev/spi*
# Should work without sudo
```

---

## Step 9: Verify LCD Pin Configuration

```bash
# Check the LCD driver has correct default pins
grep -A 5 "def __init__" src/lcd_spi_driver.py | head -10

# Should show dc_pin=24, rst_pin=25 in the defaults

# Check face_display.py reads from config
grep -A 10 "spi_config = config" src/face_display.py

# Should show it's reading from settings.yaml
```

---

## Step 10: Test LCD Driver Directly

```bash
# Make sure venv is activated
source venv/bin/activate

# Test the SPI LCD driver
python3 src/lcd_spi_driver.py
```

**Expected Output:**
```
LCD initialized successfully!
Test 1: Clear to black...
Test 2: Clear to white...
Test 3: Display test pattern...
Test 4: Display face image...
Test complete!
```

**Expected Behavior:**
- LCD should show: black → white → red → green → blue → face image
- If nothing shows, check pin connections (DC=24, RST=25)
- If garbage shows, try reducing SPI speed in settings.yaml

---

## Step 11: Test Face Display Module

```bash
# Make sure venv is activated
source venv/bin/activate

# Test face display (will use SPI driver automatically)
python3 src/face_display.py
```

**Expected Output:**
```
Using direct SPI driver for LCD (Pi 5 compatible)
  SPI: bus=0, device=0
  Pins: DC=24, RST=25, BL=18
  Speed: 32 MHz, Rotation: 1
Loaded face: happy
Loaded face: sad
...
Testing all expressions...
Displaying: happy
Displaying: sad
...
Test complete!
```

**Expected Behavior:**
- LCD should cycle through all 7 face expressions
- Each expression should display for 2 seconds

---

## Step 12: Verify Pin Configuration in Settings

```bash
# View the complete SPI configuration
cat config/settings.yaml

# The display.spi section should show:
#   spi:
#     bus: 0
#     device: 0
#     dc_pin: 24
#     rst_pin: 25
#     bl_pin: 18
#     speed_hz: 32000000
#     rotation: 1
```

**If pins are different on your LCD**, edit the file:
```bash
nano config/settings.yaml
# Change dc_pin, rst_pin, or other values as needed
# Save: Ctrl+X, Y, Enter
```

---

## Step 13: Test Full Application (Optional)

```bash
# Make sure venv is activated
source venv/bin/activate

# Make sure .env file has your API key
cat .env
# Should show: GEMINI_API_KEY=your_key_here

# Test in text mode first (no microphone needed)
python3 src/main.py --text
```

**Expected:**
- LCD should show face expressions
- You can type questions and get responses
- Servos should move (if connected)

---

## Troubleshooting Commands

### If LCD Shows Nothing

```bash
# 1. Check GPIO pins are correct
cat config/settings.yaml | grep -A 7 "spi:"

# 2. Check physical connections
#    DC pin should be GPIO 24
#    RST pin should be GPIO 25
#    BL pin should be GPIO 18

# 3. Test GPIO pins manually (optional)
python3 -c "
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(24, GPIO.OUT)
GPIO.output(24, GPIO.HIGH)
print('GPIO 24 set HIGH')
GPIO.cleanup()
"
```

### If LCD Shows Garbage

```bash
# Try reducing SPI speed
nano config/settings.yaml
# Change speed_hz: 32000000 to speed_hz: 16000000
# Save and test again
```

### If SPI Permission Denied

```bash
# Add user to spi group
sudo usermod -a -G spi $USER
newgrp spi

# Or run with sudo (not recommended for production)
sudo python3 src/lcd_spi_driver.py
```

### If Import Errors

```bash
# Make sure venv is activated
source venv/bin/activate

# Reinstall dependencies
pip install --upgrade spidev RPi.GPIO

# Verify installation
python3 -c "import spidev; import RPi.GPIO; print('OK')"
```

### If Code Not Updated from GitHub

```bash
# Check current branch
git branch

# Check remote URL
git remote -v

# Force pull (if needed)
git fetch origin
git reset --hard origin/main

# WARNING: This will overwrite local changes!
```

---

## Quick Verification Checklist

Run these commands to verify everything is set up correctly:

```bash
# 1. Code is updated
cd ~/Ash-1
git log --oneline -1
# Should show recent commit

# 2. Config has SPI settings
grep -A 7 "spi:" config/settings.yaml
# Should show pin configuration

# 3. SPI is enabled
ls -l /dev/spi*
# Should show /dev/spidev0.0 and /dev/spidev0.1

# 4. Dependencies installed
source venv/bin/activate
pip list | grep spidev
# Should show spidev package

# 5. LCD driver works
python3 src/lcd_spi_driver.py
# Should show test patterns on LCD
```

---

## Summary of Pin Configuration

After following this guide, your LCD should use:

- **DC Pin:** GPIO 24 (Data/Command)
- **RST Pin:** GPIO 25 (Reset)
- **BL Pin:** GPIO 18 (Backlight)
- **SPI Bus:** 0
- **SPI Device:** 0
- **SPI Speed:** 32 MHz
- **Rotation:** 1 (90 degrees)

All configured in: `config/settings.yaml`

---

## Next Steps

1. ✅ Code updated from GitHub
2. ✅ SPI enabled and working
3. ✅ Dependencies installed
4. ✅ LCD pins configured (DC=24, RST=25)
5. ✅ LCD driver tested
6. ✅ Face display tested
7. ✅ Ready to run full application!

Run the full application:
```bash
source venv/bin/activate
python3 src/main.py
```

---

**Last Updated:** Based on LCD pin fix (DC=24, RST=25, BUS=0, DEV=0, SPD=32MHz, ROT=1)
**For:** Raspberry Pi 5 with 3.5" ILI9486 LCD Display

