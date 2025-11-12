# Ash Robot - Hardware Deployment Plan

Complete step-by-step guide to connect software with hardware on Raspberry Pi 5.

## 📋 Pre-Deployment Checklist

### Hardware Inventory
- [ ] Raspberry Pi 5 (4GB+ RAM)
- [ ] 3.5" LCD Display (MPI3501, ILI9486)
- [ ] PCA9685 Servo Driver Board
- [ ] 2× MG995 Servo Motors
- [ ] 5V 2A+ Power Supply (for servos) - **SEPARATE from Pi power!**
- [ ] Raspberry Pi 5 Official Power Supply (5V 3A USB-C)
- [ ] MicroSD Card (32GB+, Class 10) with Raspberry Pi OS
- [ ] USB Microphone
- [ ] USB Speaker (or 3.5mm with adapter)
- [ ] Jumper Wires (Female-to-Female, ~10 pieces)
- [ ] Breadboard (optional, for prototyping)

### Software Prerequisites
- [ ] Raspberry Pi OS installed on SD card
- [ ] Pi booted and accessible (SSH or direct)
- [ ] Internet connection on Pi
- [ ] Gemini API key ready
- [ ] Face images ready (7 PNG files, 480×320)

### Tools Needed
- [ ] Screwdriver (if needed for servo mounting)
- [ ] Multimeter (optional, for voltage checks)
- [ ] Wire strippers (if needed)

---

## 🎯 Deployment Phases

### Phase 1: Raspberry Pi OS Setup
### Phase 2: Hardware Wiring (No Power)
### Phase 3: Software Deployment
### Phase 4: Component Testing (One at a Time)
### Phase 5: Integration Testing
### Phase 6: Full System Test

---

## Phase 1: Raspberry Pi OS Setup

### Step 1.1: Flash Raspberry Pi OS

1. Download Raspberry Pi Imager: https://www.raspberrypi.com/software/
2. Insert microSD card into computer
3. Open Raspberry Pi Imager
4. Click "Choose OS" → Select "Raspberry Pi OS (64-bit)"
5. Click "Choose Storage" → Select your microSD card
6. Click gear icon (⚙️) to configure:
   - **Enable SSH**: ✓
   - **Set username**: `pi` (or your choice)
   - **Set password**: (choose secure password)
   - **Configure WiFi**: (optional, or use Ethernet)
   - **Set locale**: Your timezone
7. Click "Write" and wait for completion

### Step 1.2: First Boot & Network Setup

1. Insert SD card into Pi 5
2. Connect Pi to power (USB-C)
3. Connect to network (Ethernet or WiFi)
4. Wait for boot (green LED should blink)
5. Find Pi's IP address:
   ```bash
   # On Mac/Linux:
   ping raspberrypi.local
   # Or check router admin page
   ```
6. SSH into Pi:
   ```bash
   ssh pi@raspberrypi.local
   # Or: ssh pi@<IP_ADDRESS>
   ```

### Step 1.3: Initial System Update

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Reboot
sudo reboot
```

**Wait for reboot, then SSH back in.**

---

## Phase 2: Hardware Wiring (NO POWER YET!)

⚠️ **IMPORTANT: Do NOT power on anything until all wiring is complete and verified!**

### Step 2.1: LCD Display Connection

**Physical Setup:**
1. **Power OFF** Raspberry Pi (unplug USB-C)
2. Locate GPIO header on Pi 5 (40 pins)
3. Identify Pin 1 (square pad, usually marked, top-left)
4. Align LCD's 26-pin connector with Pi's pins 1-26
5. **Gently** press LCD onto GPIO header
   - Should sit flush against the board
   - No pins should be bent
   - Connector should be fully seated

**Verification:**
- ✅ LCD sits flush on GPIO header
- ✅ No pins visible between LCD and Pi
- ✅ Pins 27-40 remain accessible (below LCD)

**⚠️ Do NOT power on yet!**

### Step 2.2: PCA9685 Servo Driver Wiring

**Required Connections (4 wires):**

| PCA9685 Pin | → | Raspberry Pi Pin | Wire Color (suggestion) |
|-------------|---|------------------|------------------------|
| VCC         | → | Pin 1            | Red (3.3V) |
| GND         | → | Pin 6            | Black (Ground) |
| SDA         | → | Pin 3            | Yellow (Data) |
| SCL         | → | Pin 5            | Green (Clock) |

**Physical Steps:**
1. **Pi is still OFF**
2. Use female-to-female jumper wires
3. Connect PCA9685 VCC → Pi Pin 1 (3.3V)
4. Connect PCA9685 GND → Pi Pin 6 (GND)
5. Connect PCA9685 SDA → Pi Pin 3 (GPIO 2)
6. Connect PCA9685 SCL → Pi Pin 5 (GPIO 3)

**⚠️ Critical Notes:**
- Use **3.3V** (Pin 1), NOT 5V!
- Pins 3 and 5 are I2C (not used by LCD)
- Double-check connections before proceeding

**Verification Checklist:**
- ✅ 4 wires connected correctly
- ✅ No loose connections
- ✅ Wires not touching each other
- ✅ PCA9685 board stable (not moving)

### Step 2.3: Servo Power Supply Setup

**⚠️ CRITICAL: This is the most common mistake!**

**What You Need:**
- Separate 5V power supply (2A minimum, 3A recommended)
- NOT the Pi's power supply!
- Can be USB power bank, wall adapter, or bench supply

**Connections:**

1. **Servo Power Supply (+) → PCA9685 V+**
   - Connect red/positive wire from power supply to PCA9685 V+ terminal

2. **Servo Power Supply (-) → PCA9685 GND**
   - Connect black/negative wire from power supply to PCA9685 GND terminal

3. **Servo Power Supply (-) → Raspberry Pi GND** ⚠️ **COMMON GROUND!**
   - **ALSO** connect the same black/negative wire to Pi GND
   - Can use Pin 6, 9, 14, 20, 25, or 39
   - **This is essential!** Without it, servos won't work properly

**Visual Connection:**
```
Servo Power Supply
    (+) ──────────→ PCA9685 V+
    (-) ────┬─────→ PCA9685 GND
            │
            └─────→ Pi GND (Pin 6)  ← COMMON GROUND!
```

**Verification:**
- ✅ Power supply (+) to PCA9685 V+
- ✅ Power supply (-) to PCA9685 GND
- ✅ Power supply (-) to Pi GND (common ground!)
- ✅ Power supply is **OFF** (not plugged in yet)

### Step 2.4: Servo Motor Connections

**MG995 Servo Wire Colors:**
- **Red**: Power (+5V)
- **Brown/Black**: Ground
- **Orange/Yellow**: Signal (PWM control)

**Left Arm Servo (Channel 0):**
1. Plug servo connector into PCA9685 Channel 0
2. Ensure correct orientation:
   - Signal wire (orange/yellow) should be on the inside/top
   - Red wire aligns with V+ terminal
   - Brown/black wire aligns with GND terminal

**Right Arm Servo (Channel 1):**
1. Plug servo connector into PCA9685 Channel 1
2. Same orientation as left servo

**⚠️ Do NOT connect servo power yet!**

**Verification:**
- ✅ Left servo on Channel 0
- ✅ Right servo on Channel 1
- ✅ Connectors fully seated
- ✅ Correct orientation (signal wire inside)

### Step 2.5: Audio Devices

**Microphone:**
- Plug USB microphone into any USB port on Pi
- Or use Pi's onboard microphone if available

**Speaker:**
- Plug USB speaker into any USB port on Pi
- Or use 3.5mm audio jack if available

**Verification:**
- ✅ Microphone connected
- ✅ Speaker connected
- ✅ Devices recognized (will test later)

---

## Phase 3: Software Deployment

### Step 3.1: Transfer Code to Pi

**Option A: Clone from GitHub (Recommended)**
```bash
# On Raspberry Pi (via SSH)
cd ~
git clone https://github.com/Lakshya-Inakhiya/Ash.git
cd Ash
```

**Option B: Transfer from Mac**
```bash
# On Mac
cd ~/Desktop
scp -r Ash-1 pi@raspberrypi.local:~/Ash
```

### Step 3.2: Install LCD Driver

**⚠️ Important: Ensure network connectivity before proceeding!**

```bash
# On Pi
# First, install required dependencies manually
sudo apt-get update
sudo apt-get install -y cmake build-essential git xserver-xorg-input-evdev

# Now install LCD driver
cd ~
sudo rm -rf LCD-show
git clone https://github.com/goodtft/LCD-show.git
chmod -R 755 LCD-show
cd LCD-show

# Install driver (will reboot)
sudo ./LCD35-show
```

**⚠️ If you see "bad network, can't install cmake!!!" error:**
- Install cmake manually first: `sudo apt-get install -y cmake build-essential`
- Then re-run: `sudo ./LCD35-show`
- Or use the fix script: See `LCD_TROUBLESHOOTING.md`

**After reboot, SSH back in and rotate:**
```bash
cd ~/LCD-show
sudo ./rotate.sh 90
sudo reboot
```

**After reboot:**
- LCD should display Raspberry Pi desktop
- Resolution should be 480×320 (landscape)
- Touch screen should work (if applicable)
- Verify framebuffer: `ls -l /dev/fb*` (should show `/dev/fb1`)

### Step 3.3: Enable I2C Interface

```bash
# On Pi
sudo raspi-config
```

**Navigate:**
1. Interface Options
2. I2C
3. Enable
4. Finish
5. Reboot when prompted

**Verify I2C:**
```bash
sudo i2cdetect -y 1
```

**Expected Output:**
```
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- -- -- -- --
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
40: 40 -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
70: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
```

**The `40` indicates PCA9685 is detected!** ✅

### Step 3.4: Install System Dependencies

```bash
cd ~/Ash  # or ~/Ash-1 if you transferred from Mac

# Update package list
sudo apt-get update

# Install system packages
sudo apt-get install -y \
    python3-pip \
    python3-pil \
    i2c-tools \
    portaudio19-dev \
    python3-all-dev \
    git
```

### Step 3.5: Install Python Dependencies

```bash
# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt
```

**Note:** `pyaudio` should install successfully on Pi (has system libraries).

### Step 3.6: Configure Environment

```bash
# Create .env file
nano .env
```

**Add:**
```env
GEMINI_API_KEY=your_actual_api_key_here
```

**Save:** Ctrl+X, Y, Enter

### Step 3.7: Verify Face Images

```bash
# Check if face images exist
ls -l assets/faces/

# Should show 7 PNG files:
# happy.png, sad.png, neutral.png, listening.png, 
# speaking.png, thinking.png, error.png
```

**If missing, generate sample faces:**
```bash
python3 create_sample_faces.py
```

---

## Phase 4: Component Testing (One at a Time)

⚠️ **Test each component independently before full integration!**

### Test 4.1: LCD Display

```bash
cd ~/Ash
source venv/bin/activate  # if using venv
python3 src/face_display.py
```

**Expected:**
- ✅ Face images cycle through all 7 expressions
- ✅ Each expression displays for 2 seconds
- ✅ Images are clear and properly sized (480×320)

**If Issues:**
- **No /dev/fb1 found:** See `LCD_TROUBLESHOOTING.md` for detailed fix
- **Network error during installation:** Install cmake manually: `sudo apt-get install -y cmake build-essential`, then re-run `sudo ./LCD35-show`
- **Check framebuffer:** `ls -l /dev/fb*` (should show `/dev/fb1`)
- **Check rotation:** `cd ~/LCD-show && sudo ./rotate.sh 90`
- **Permission denied:** Add user to video group: `sudo usermod -a -G video $USER` (logout/login required)

### Test 4.2: PCA9685 Communication

**⚠️ Servo power supply should still be OFF!**

```bash
# Verify I2C detection
sudo i2cdetect -y 1
# Should show 0x40

# Test PCA9685 communication (no servos moving)
python3 src/gestures.py
```

**Expected:**
- ✅ No errors about I2C communication
- ✅ Console shows servo simulation messages
- ✅ No actual servo movement (power is off)

**If Issues:**
- Check I2C enabled: `sudo raspi-config` → Interface Options → I2C
- Check wiring: VCC→Pin1, GND→Pin6, SDA→Pin3, SCL→Pin5
- Check connections are tight

### Test 4.3: Servo Motors (With Power!)

**⚠️ Now you can power on servo supply!**

1. **Double-check all connections:**
   - ✅ Servo power supply (+) → PCA9685 V+
   - ✅ Servo power supply (-) → PCA9685 GND
   - ✅ Servo power supply (-) → Pi GND (common ground!)
   - ✅ Left servo on Channel 0
   - ✅ Right servo on Channel 1

2. **Power on servo supply** (keep Pi already running)

3. **Test servos:**
   ```bash
   python3 src/gestures.py
   ```

4. **Watch servos carefully:**
   - ✅ Should move smoothly through test sequence
   - ✅ No jittering or erratic movement
   - ✅ Should return to neutral position
   - ⚠️ If servos bind or stall, press Ctrl+C immediately!

**Expected Test Sequence:**
- Neutral (90°)
- Arms Up (45°)
- Arms Down (135°)
- Point (right up, left down)
- Wave (left arm oscillates)
- Back to Neutral

**If Issues:**
- **Jittering**: Check power supply voltage (should be stable 5V)
- **Not moving**: Check common ground connection!
- **Erratic**: Check power supply current capacity (need 2A+)
- **Binding**: Check servo arms aren't obstructed

### Test 4.4: Audio Input (Microphone)

```bash
python3 src/audio_io.py
```

**Expected:**
- ✅ Microphone detected
- ✅ Test recording works
- ✅ Speech recognition test completes

**If Issues:**
- List devices: `arecord -l`
- Test mic: `arecord -d 5 test.wav && aplay test.wav`
- Check permissions: `sudo usermod -a -G audio $USER` (then logout/login)

### Test 4.5: Audio Output (Speaker)

```bash
# Test speaker
speaker-test -t wav

# Or test via audio_io.py (will play TTS)
python3 src/audio_io.py
```

**Expected:**
- ✅ Sound plays through speaker
- ✅ TTS audio is clear

**If Issues:**
- List devices: `aplay -l`
- Check volume: `alsamixer`
- Test: `aplay test.wav` (if you recorded one)

### Test 4.6: Gemini API

```bash
# Make sure .env has your API key
python3 src/llm_client.py
```

**Expected:**
- ✅ API key loaded
- ✅ Test questions answered
- ✅ Responses are concise (1-2 sentences)

**If Issues:**
- Check `.env` file exists and has correct key
- Check internet connection: `ping google.com`
- Verify API key: https://makersuite.google.com/app/apikey

---

## Phase 5: Integration Testing

### Test 5.1: Face + Servos Together

```bash
# Run main with text mode first
python3 src/main.py --text
```

**Test gestures:**
```
You: gestures
```

**Expected:**
- ✅ Face window shows expressions
- ✅ Servos move in sync with gestures
- ✅ All 5 gestures work

### Test 5.2: Voice Input

```bash
python3 src/main.py
# (voice mode, default)
```

**Test:**
- Speak: "Hello"
- Expected: Ash waves and responds

**If Issues:**
- Check microphone permissions
- Try text mode: `python3 src/main.py --text`
- Check mic: `arecord -l`

### Test 5.3: Full Interaction Loop

```bash
python3 src/main.py --text
```

**Test Sequence:**
1. Type: `hello`
   - Expected: Wave gesture, greeting response

2. Type: `who are you`
   - Expected: Point gesture, explanation

3. Type: `greet sunil sir`
   - Expected: Wave gesture, greeting

4. Type: `gestures`
   - Expected: All 5 gestures demo

5. Type: `quit`
   - Expected: Clean exit

---

## Phase 6: Full System Test

### Test 6.1: Complete Conversation (Text Mode)

```bash
python3 src/main.py --text
```

**Full Test:**
```
You: hello
→ Wave + greeting

You: what is your name
→ Point + explanation

You: greet my friend
→ Wave + greeting

You: that's awesome
→ Arms up + celebration

You: quit
→ Clean exit
```

**Verify:**
- ✅ All gestures trigger correctly
- ✅ Face expressions match context
- ✅ Responses are appropriate
- ✅ Audio plays (TTS)
- ✅ Clean shutdown

### Test 6.2: Complete Conversation (Voice Mode)

```bash
python3 src/main.py
```

**Test:**
- Speak: "Hello"
- Speak: "What is 2 + 2?"
- Speak: "Greet Sunil sir"
- Type: `quit` (or speak "quit")

**Verify:**
- ✅ Voice recognition works
- ✅ Gestures match speech context
- ✅ TTS plays responses
- ✅ All components work together

---

## 🔧 Troubleshooting Guide

### LCD Not Working

**Symptoms:** Blank screen, distorted image, wrong resolution

**Solutions:**
```bash
# Reinstall LCD driver
cd ~/LCD-show
sudo ./LCD35-show
sudo reboot

# After reboot, rotate:
cd ~/LCD-show
sudo ./rotate.sh 90

# Check framebuffer exists:
ls -l /dev/fb1

# Test display:
python3 src/face_display.py
```

### Servos Not Moving

**Symptoms:** No movement, jittering, erratic behavior

**Checklist:**
1. **I2C Communication:**
   ```bash
   sudo i2cdetect -y 1  # Should show 0x40
   ```

2. **Power Supply:**
   - Voltage: Should be 5V (check with multimeter)
   - Current: Should be 2A+ capacity
   - Connected: V+ to PCA9685 V+, GND to PCA9685 GND

3. **Common Ground:**
   - ⚠️ **MOST COMMON ISSUE!**
   - Servo power (-) must connect to BOTH:
     - PCA9685 GND
     - Raspberry Pi GND (Pin 6)
   - Without this, servos won't work!

4. **Servo Connections:**
   - Left servo on Channel 0
   - Right servo on Channel 1
   - Connectors fully seated
   - Signal wire (orange/yellow) on inside

5. **Test Servos:**
   ```bash
   python3 src/gestures.py
   ```

### Microphone Not Working

**Symptoms:** "Microphone not available", no voice input

**Solutions:**
```bash
# List audio devices
arecord -l

# Test microphone
arecord -d 5 test.wav
aplay test.wav

# Add user to audio group
sudo usermod -a -G audio $USER
# Logout and login again

# Check permissions
# System Settings → Privacy → Microphone (if GUI available)
```

### Speaker Not Working

**Symptoms:** No sound output

**Solutions:**
```bash
# List output devices
aplay -l

# Test speaker
speaker-test -t wav

# Adjust volume
alsamixer

# Set default device (if multiple)
# Edit /etc/asound.conf or ~/.asoundrc
```

### Gemini API Errors

**Symptoms:** "API key not set", rate limit errors

**Solutions:**
```bash
# Check .env file
cat .env
# Should show: GEMINI_API_KEY=your_key_here

# Verify key is correct
# Get new key: https://makersuite.google.com/app/apikey

# Test API:
python3 src/llm_client.py
```

### Import Errors

**Symptoms:** "No module named X"

**Solutions:**
```bash
# Activate virtual environment
source venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt

# Check Python version
python3 --version  # Should be 3.9+

# Install missing packages individually
pip install <package_name>
```

---

## ⚠️ Safety Reminders

### Before Powering On:
- ✅ All connections double-checked
- ✅ Servo power supply is OFF
- ✅ Common ground connected
- ✅ No short circuits
- ✅ Wires not touching

### During Testing:
- ⚠️ Watch servos carefully - stop if they bind
- ⚠️ Don't obstruct servo arms
- ⚠️ Monitor power supply temperature
- ⚠️ Check for smoke or burning smell (immediately power off!)

### Power Supply Safety:
- ⚠️ **NEVER** power servos from Pi's 5V rail
- ⚠️ Use separate 5V 2A+ supply for servos
- ⚠️ Always use common ground
- ⚠️ Check polarity before connecting

---

## 📊 Testing Checklist

Use this checklist to verify everything works:

### Hardware Connections
- [ ] LCD connected to GPIO pins 1-26
- [ ] PCA9685 VCC → Pi Pin 1 (3.3V)
- [ ] PCA9685 GND → Pi Pin 6
- [ ] PCA9685 SDA → Pi Pin 3
- [ ] PCA9685 SCL → Pi Pin 5
- [ ] Servo power (+) → PCA9685 V+
- [ ] Servo power (-) → PCA9685 GND
- [ ] Servo power (-) → Pi GND (common ground!)
- [ ] Left servo → Channel 0
- [ ] Right servo → Channel 1
- [ ] USB microphone connected
- [ ] USB speaker connected

### Software Setup
- [ ] Raspberry Pi OS installed
- [ ] LCD driver installed
- [ ] I2C enabled
- [ ] Python dependencies installed
- [ ] .env file with API key
- [ ] Face images present (7 PNGs)

### Component Tests
- [ ] LCD display works (face_display.py)
- [ ] PCA9685 detected (i2cdetect shows 0x40)
- [ ] Servos move (gestures.py)
- [ ] Microphone works (audio_io.py)
- [ ] Speaker works (TTS test)
- [ ] Gemini API works (llm_client.py)

### Integration Tests
- [ ] Face + Servos together
- [ ] Voice input works
- [ ] Text input works
- [ ] Gestures trigger correctly
- [ ] Full conversation loop works
- [ ] Clean shutdown works

---

## 🎯 Success Criteria

**You're ready when:**
- ✅ All individual components test successfully
- ✅ Face displays correctly on LCD
- ✅ Servos move smoothly through all gestures
- ✅ Voice input recognizes speech
- ✅ TTS plays responses clearly
- ✅ Gemini API responds appropriately
- ✅ Intelligent gestures work (wave on "hello", etc.)
- ✅ Full conversation loop works end-to-end
- ✅ Clean exit works

---

## 🚀 Next Steps After Deployment

1. **Fine-tune Gesture Angles**
   - Adjust angles in `config/settings.yaml`
   - Test physical arm positions
   - Ensure no binding or obstruction

2. **Calibrate Audio**
   - Adjust microphone sensitivity
   - Set speaker volume
   - Test in your environment

3. **Customize Face Images**
   - Replace sample faces with custom designs
   - Ensure 480×320 resolution
   - Test all expressions

4. **Optimize Performance**
   - Monitor CPU usage
   - Check memory usage
   - Adjust cooldown periods if needed

5. **Add Enhancements**
   - Wake word detection
   - More gestures
   - Camera integration
   - Local LLM option

---

## 📞 Support Resources

- **Wiring Guide**: See `HARDWARE_WIRING.md`
- **Quick Start**: See `QUICKSTART.md`
- **Usage Guide**: See `USAGE.md`
- **Troubleshooting**: See `README.md` troubleshooting section
- **GitHub Issues**: https://github.com/Lakshya-Inakhiya/Ash/issues

---

## ✅ Deployment Complete!

Once all tests pass, your Ash robot is fully operational! 🤖✨

**Enjoy your AI robot companion!**

