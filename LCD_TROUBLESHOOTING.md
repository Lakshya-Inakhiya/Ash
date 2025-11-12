# LCD Driver Troubleshooting Guide

## Problem: /dev/fb1 Not Found After LCD35-show Installation

### Symptoms
- `ls -l /dev/fb*` returns "No such file or directory"
- LCD screen is blank or not working
- Face display test runs in simulation mode only
- Network error during `LCD35-show` installation: "bad network, can't install cmake!!!"
- **On Raspberry Pi 5:** Error: "fatal error: bcm_host.h: No such file or directory"

### ⚠️ IMPORTANT: Raspberry Pi 5 Incompatibility

**The `goodtft/LCD-show` repository does NOT work on Raspberry Pi 5!**

The `LCD35-show` script uses old VideoCore APIs (`bcm_host.h`, `libraspberrypi-dev`) that don't exist on Pi 5. If you see errors like:

```
fatal error: bcm_host.h: No such file or directory
Package 'libraspberrypi-dev' has no installation candidate
```

**You need to use a different approach for Pi 5.** See `PI5_LCD_FIX.md` and `PI5_SETUP_GUIDE.md` for Pi 5 specific solutions.

### Root Cause

**For Raspberry Pi 4 and earlier:**
The `LCD35-show` script failed to install `cmake` due to network issues, preventing the LCD driver from being compiled and installed.

**For Raspberry Pi 5:**
The `LCD35-show` script is **fundamentally incompatible** with Pi 5 because it uses deprecated VideoCore APIs that don't exist on Pi 5. Even with cmake installed, the driver won't compile because `bcm_host.h` and other VideoCore headers don't exist on Pi 5.

### Solution

#### Option 1: Manual Fix (Recommended)

1. **SSH into your Raspberry Pi:**
   ```bash
   ssh lakshya@milo.local
   ```

2. **Update package list and install dependencies manually:**
   ```bash
   sudo apt-get update
   sudo apt-get install -y cmake build-essential git xserver-xorg-input-evdev
   ```

3. **Reinstall LCD driver:**
   ```bash
   cd ~/LCD-show
   sudo ./LCD35-show
   ```

4. **After reboot, rotate the display:**
   ```bash
   cd ~/LCD-show
   sudo ./rotate.sh 90
   sudo reboot
   ```

5. **Verify framebuffer exists:**
   ```bash
   ls -l /dev/fb*
   ```
   Should show `/dev/fb0` and `/dev/fb1`

#### Option 2: Use Fix Script

1. **Transfer the fix script to Pi:**
   ```bash
   # On your Mac
   scp fix_lcd_driver.sh lakshya@milo.local:~/
   ```

2. **SSH into Pi and run the script:**
   ```bash
   ssh lakshya@milo.local
   chmod +x ~/fix_lcd_driver.sh
   ~/fix_lcd_driver.sh
   ```

3. **After reboot, rotate display:**
   ```bash
   cd ~/LCD-show
   sudo ./rotate.sh 90
   sudo reboot
   ```

#### Option 3: Clean Reinstall

If the above doesn't work, try a clean reinstall:

1. **Remove existing LCD-show directory:**
   ```bash
   sudo rm -rf ~/LCD-show
   ```

2. **Install dependencies:**
   ```bash
   sudo apt-get update
   sudo apt-get install -y cmake build-essential git xserver-xorg-input-evdev
   ```

3. **Clone and install LCD driver:**
   ```bash
   cd ~
   git clone https://github.com/goodtft/LCD-show.git
   chmod -R 755 LCD-show
   cd LCD-show
   sudo ./LCD35-show
   ```

4. **After reboot, rotate:**
   ```bash
   cd ~/LCD-show
   sudo ./rotate.sh 90
   sudo reboot
   ```

### Verification Steps

After installation and reboot:

1. **Check framebuffer devices:**
   ```bash
   ls -l /dev/fb*
   ```
   Expected output:
   ```
   crw-rw---- 1 root video 29, 0 Nov 12 10:00 /dev/fb0
   crw-rw---- 1 root video 29, 1 Nov 12 10:00 /dev/fb1
   ```

2. **Check display resolution:**
   ```bash
   fbset -fb /dev/fb1
   ```
   Should show 480x320 resolution

3. **Test face display:**
   ```bash
   cd ~/Ash
   source venv/bin/activate
   python3 src/face_display.py
   ```
   Should display faces on LCD (not just pygame window)

### Common Issues

#### Issue 1: Network Still Not Working
If you still have network issues:

```bash
# Check network connection
ping -c 3 google.com

# If not working, check WiFi/Ethernet
ip addr show

# Restart networking (if needed)
sudo systemctl restart networking
```

#### Issue 2: Permission Denied on /dev/fb1
If you get permission errors:

```bash
# Add user to video group
sudo usermod -a -G video $USER

# Logout and login again, or:
newgrp video

# Verify group membership
groups
```

#### Issue 3: LCD Shows Wrong Orientation
If display is rotated incorrectly:

```bash
cd ~/LCD-show
sudo ./rotate.sh 90    # Rotate 90 degrees
# Or try other angles: 180, 270, 0
sudo reboot
```

#### Issue 4: LCD Shows Garbage or Distorted Image
If display shows garbage:

```bash
# Reinstall driver
cd ~/LCD-show
sudo ./LCD35-show
sudo reboot

# After reboot, check if correct model
# For 3.5" LCD, use LCD35-show (not LCD28-show, etc.)
```

### Alternative: Check LCD Model

Make sure you're using the correct driver for your LCD:

- **3.5" LCD (MPI3501, ILI9486)**: Use `LCD35-show`
- **2.8" LCD**: Use `LCD28-show`
- **Other sizes**: Check LCD-show repository for correct script

### Additional Resources

- LCD-show GitHub: https://github.com/goodtft/LCD-show
- Raspberry Pi Framebuffer: https://www.raspberrypi.org/documentation/configuration/device-tree.md
- Troubleshooting: Check `HARDWARE_DEPLOYMENT_PLAN.md` Section 4.1

### Still Not Working?

If none of the above works:

1. **Check LCD hardware connection:**
   - Ensure LCD is properly seated on GPIO pins 1-26
   - Check for bent pins
   - Verify power connections

2. **Check system logs:**
   ```bash
   dmesg | grep -i lcd
   dmesg | grep -i fb
   journalctl -u display-manager
   ```

3. **Try different LCD driver:**
   - Some LCDs may need different drivers
   - Check your LCD's datasheet for driver chip (ILI9486, etc.)

4. **Verify Raspberry Pi model:**
   ```bash
   cat /proc/device-tree/model
   ```
   Make sure LCD driver is compatible with Pi 5

### Quick Reference Commands

```bash
# Check framebuffer
ls -l /dev/fb*

# Install dependencies
sudo apt-get update && sudo apt-get install -y cmake build-essential

# Reinstall LCD driver
cd ~/LCD-show && sudo ./LCD35-show

# Rotate display
cd ~/LCD-show && sudo ./rotate.sh 90 && sudo reboot

# Test display
python3 src/face_display.py

# Check permissions
groups
sudo usermod -a -G video $USER
```

---

**Last Updated:** November 2025
**For:** Raspberry Pi 5 with 3.5" LCD Display

