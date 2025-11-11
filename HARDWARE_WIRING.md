# Ash Robot - Hardware Wiring Guide

This document provides detailed wiring instructions for the Ash robot hardware.

## ⚠️ Safety First

**CRITICAL WARNINGS:**
1. **NEVER** connect servos to Pi's 5V pins - they draw too much current
2. **ALWAYS** use a separate 5V power supply for servos (2A minimum)
3. **ALWAYS** connect common ground between Pi and servo power supply
4. Double-check all connections before powering on
5. Start with servos unplugged to test PCA9685 communication first

## Bill of Materials

| Component | Quantity | Notes |
|-----------|----------|-------|
| Raspberry Pi 5 | 1 | 4GB RAM recommended |
| 3.5" LCD Display (MPI3501) | 1 | ILI9486 driver, SPI interface |
| PCA9685 Servo Driver | 1 | 16-channel, I2C interface |
| MG995 Servo Motors | 2 | High-torque servos |
| 5V Power Supply for Servos | 1 | 2A minimum, 3A recommended |
| USB Microphone | 1 | Any USB mic |
| USB Speaker | 1 | Or 3.5mm speaker with USB adapter |
| Jumper Wires (F-F) | ~10 | Female-to-female |
| MicroSD Card | 1 | 32GB+, Class 10 |

## Connection Overview

```
         ┌──────────────────────────────────────┐
         │                                      │
         │      Raspberry Pi 5                  │
         │                                      │
         │  GPIO Pins 1-26 ← LCD Display        │
         │                                      │
         │  Pin 3 (SDA) ──────────┐            │
         │  Pin 5 (SCL) ────────┐ │            │
         │  Pin 6 (GND) ──────┐ │ │            │
         └────────────────────┼─┼─┼────────────┘
                              │ │ │
                              │ │ └─────┐
                              │ └─────┐ │
                              └─────┐ │ │
         ┌──────────────────────┐ │ │ │
         │    PCA9685           │ │ │ │
         │  Servo Driver Board  │ │ │ │
         │                      │ │ │ │
         │  VCC ←───────────────┼─┘ │ │
         │  SDA ←───────────────┼───┘ │
         │  SCL ←───────────────┼─────┘
         │  GND ←───────────────┼────────┐
         │                      │        │
         │  V+  ←───────────────┼─────┐  │
         │  GND ←───────────────┘     │  │
         │                            │  │
         │  Channel 0 ──┬→ Left Arm  │  │
         │              │             │  │
         │  Channel 1 ──┼→ Right Arm │  │
         │              │             │  │
         └──────────────┼─────────────┼──┘
                        │             │
                        │             │
              ┌─────────┴────────┐    │
              │                  │    │
              │  5V Servo Power  │    │
              │     Supply       │    │
              │   (2A minimum)   │    │
              │                  │    │
              │  (+) ─────────────────┘
              │  (-) ──────────────────────┐
              └─────────────────────────────┼──────────┐
                                            │          │
                                            └→ Pi GND  │
                                                       │
                                   (Common Ground!)    │
                                                       │
              ┌──────────────┐        ┌───────────────┘
              │  Left Servo  │        │  Right Servo
              │   (MG995)    │        │   (MG995)
              │              │        │
              │ Red    → +5V │        │ Red    → +5V
              │ Brown  → GND │        │ Brown  → GND
              │ Orange → Ch0 │        │ Orange → Ch1
              └──────────────┘        └──────────────┘
```

## Step-by-Step Wiring

### Step 1: LCD Display

The 3.5" LCD plugs directly onto the Raspberry Pi GPIO header.

**Connection:**
- Align the LCD's 26-pin connector with pins 1-26 on the Pi
- Pin 1 (3.3V) is the square pad on the Pi, usually marked
- Gently press the LCD onto the GPIO pins until firmly seated

**Verification:**
- LCD should sit flush against the GPIO header
- No pins should be bent or misaligned
- GPIO pins 27-40 remain accessible below the LCD

### Step 2: PCA9685 Servo Driver

Connect the PCA9685 to the Raspberry Pi I2C bus.

**Pin Mapping:**

| PCA9685 Pin | → | Raspberry Pi Pin | GPIO Function |
|-------------|---|------------------|---------------|
| VCC         | → | Pin 1            | 3.3V Power    |
| GND         | → | Pin 6            | Ground        |
| SDA         | → | Pin 3            | GPIO 2 (SDA)  |
| SCL         | → | Pin 5            | GPIO 3 (SCL)  |

**Physical Connection:**
1. Use female-to-female jumper wires
2. Connect VCC (PCA9685) to Pin 1 (Pi) - 3.3V
3. Connect GND (PCA9685) to Pin 6 (Pi) - Ground
4. Connect SDA (PCA9685) to Pin 3 (Pi) - I2C Data
5. Connect SCL (PCA9685) to Pin 5 (Pi) - I2C Clock

**Important Notes:**
- Use 3.3V for VCC, NOT 5V (PCA9685 logic is 3.3V compatible)
- Pins 3 and 5 are specifically for I2C communication
- The LCD doesn't use these I2C pins, so they're available

### Step 3: Servo Power Supply

Connect the servo power supply to the PCA9685.

**CRITICAL: This is where most mistakes happen!**

**Power Supply Setup:**
1. Connect servo power supply (+) to PCA9685 V+
2. Connect servo power supply (-) to PCA9685 GND
3. **ALSO** connect servo power supply (-) to Raspberry Pi GND (Pin 6, 9, 14, 20, 25, or 39)

**Why Common Ground?**
- The Pi sends 3.3V logic signals to PCA9685
- PCA9685 converts them to servo PWM signals (powered by servo supply)
- Without common ground, voltage levels are undefined
- Servos may not work or behave erratically

**Visual:**
```
Pi GND ──┐
         ├──→ Common Ground Rail
PCA GND ─┤
         │
Servo ─  ┘
Supply (-)
```

### Step 4: Connect Servos

Connect each MG995 servo to the PCA9685.

**MG995 Wire Colors:**
- **Red**: Power (+5V) - connects to servo power supply
- **Brown/Black**: Ground - connects to servo power supply
- **Orange/Yellow**: Signal - connects to PCA9685 channel

**Left Arm Servo (Channel 0):**
1. Plug servo connector into PCA9685 Channel 0
2. Ensure correct orientation (signal wire to top/inside)
3. Red wire should align with V+ on the terminal block

**Right Arm Servo (Channel 1):**
1. Plug servo connector into PCA9685 Channel 1
2. Ensure correct orientation (signal wire to top/inside)
3. Red wire should align with V+ on the terminal block

**Physical Arrangement:**
```
PCA9685 Channel Header:
┌──────────────────┐
│ ●  GND           │  ← Ground (Brown/Black)
│ ●  V+            │  ← Power (Red)
│ ●  Signal        │  ← Control (Orange/Yellow)
└──────────────────┘
     ↑
Plug servo connector here
```

### Step 5: Audio Devices

**Microphone:**
- Plug USB microphone into any available USB port on Pi

**Speaker:**
- Plug USB speaker into any available USB port on Pi
- Or use 3.5mm audio jack if your speaker has one

### Step 6: Power Connections Summary

**Before powering on, verify:**

✅ LCD connected to GPIO pins 1-26  
✅ PCA9685 VCC to Pi Pin 1 (3.3V)  
✅ PCA9685 GND to Pi Pin 6 (GND)  
✅ PCA9685 SDA to Pi Pin 3  
✅ PCA9685 SCL to Pi Pin 5  
✅ Servo power supply (+) to PCA9685 V+  
✅ Servo power supply (-) to PCA9685 GND  
✅ Servo power supply (-) to Pi GND (common ground!)  
✅ Left servo to PCA9685 Channel 0  
✅ Right servo to PCA9685 Channel 1  
✅ USB microphone plugged in  
✅ USB speaker plugged in  

## Power-On Sequence

**Recommended power-up order:**

1. **First**: Ensure servo power supply is OFF
2. Power on Raspberry Pi and let it boot
3. SSH into Pi or connect monitor/keyboard
4. Run: `sudo i2cdetect -y 1` to verify PCA9685 detected (should show 0x40)
5. Test PCA9685 communication: `python3 src/gestures.py`
6. **Only after successful test**: Turn on servo power supply
7. Servos should initialize to neutral position (90°)

## Verification Tests

### Test 1: I2C Communication

```bash
sudo i2cdetect -y 1
```

Expected output:
```
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- -- -- -- --
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
40: 40 -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
70: -- -- -- -- -- -- -- --
```

The `40` indicates PCA9685 is detected at address 0x40.

### Test 2: LCD Display

```bash
cd ~/Desktop/Ash-1
python3 src/face_display.py
```

Should cycle through test patterns (or face images if present).

### Test 3: Servo Movement

```bash
cd ~/Desktop/Ash-1
python3 src/gestures.py
```

Servos should move through test sequence. **Watch servos carefully** - if they bind or stall, press Ctrl+C immediately.

### Test 4: Audio

```bash
cd ~/Desktop/Ash-1
python3 src/audio_io.py
```

Should play test audio and test microphone.

## Troubleshooting

### PCA9685 Not Detected

**Symptom:** `i2cdetect -y 1` shows no device at 0x40

**Solutions:**
- Verify I2C is enabled: `sudo raspi-config` → Interface Options → I2C
- Check SDA/SCL connections (Pins 3 and 5)
- Check VCC connection (Pin 1, 3.3V)
- Check GND connection (Pin 6)
- Reboot Pi: `sudo reboot`

### Servos Not Moving

**Symptom:** Servos don't respond to commands

**Solutions:**
- Verify servo power supply is ON
- Check V+ and GND connections to PCA9685
- Verify common ground between Pi and servo supply
- Check servo connectors are fully plugged in
- Verify correct channel (0 and 1)
- Try: `sudo i2cdetect -y 1` to ensure PCA9685 is detected

### Servos Jittering

**Symptom:** Servos vibrate or shake

**Solutions:**
- Check servo power supply voltage (should be stable 5V)
- Ensure power supply provides adequate current (2A minimum)
- Check for loose wiring
- Verify common ground connection
- Try shorter wires between PCA9685 and servos

### LCD Not Working

**Symptom:** LCD is blank or shows garbage

**Solutions:**
- Verify LCD is fully seated on GPIO pins
- Check Pin 1 alignment (square pad)
- Reinstall LCD driver: `cd ~/LCD-show && sudo ./LCD35-show`
- Check `/dev/fb1` exists: `ls -l /dev/fb*`
- Verify rotation: `cd ~/LCD-show && sudo ./rotate.sh 90`

### No Audio Input/Output

**Symptom:** Microphone or speaker not working

**Solutions:**
- List devices: `arecord -l` (mic) and `aplay -l` (speaker)
- Check USB connections
- Try different USB port
- Update audio config: `sudo apt-get install pulseaudio`
- Test speaker: `speaker-test -t wav`
- Test mic: `arecord -d 5 test.wav && aplay test.wav`

## Advanced: Multiple Servos

The PCA9685 supports up to 16 servos. To add more:

1. Connect servos to additional channels (2-15)
2. Update `config/settings.yaml` with new channels
3. Add gesture functions in `src/gestures.py`
4. Ensure servo power supply can handle additional current

**Current per servo:**
- Idle: ~10mA
- Moving: 100-300mA
- Stalled: 500-1000mA (avoid!)

Example: 4 servos = 1A typical, 2A peak, 3A supply recommended

## Pin Reference Tables

### Raspberry Pi 5 GPIO Pinout (Relevant Pins)

```
    3.3V  [ 1] [ 2]  5V
GPIO 2/SDA [ 3] [ 4]  5V
GPIO 3/SCL [ 5] [ 6]  GND
   GPIO 4  [ 7] [ 8]  GPIO 14
      GND  [ 9] [10]  GPIO 15
  GPIO 17  [11] [12]  GPIO 18
  GPIO 27  [13] [14]  GND
  GPIO 22  [15] [16]  GPIO 23
    3.3V   [17] [18]  GPIO 24
  GPIO 10  [19] [20]  GND
   GPIO 9  [21] [22]  GPIO 25
  GPIO 11  [23] [24]  GPIO 8
      GND  [25] [26]  GPIO 7
       ↑
    (LCD covers pins 1-26)
```

### PCA9685 Pinout

```
┌─────────────────────────┐
│  VCC   GND   SDA   SCL  │  ← Logic pins
│  ●     ●     ●     ●    │
│                         │
│  V+    GND              │  ← Power terminal
│  ●●●   ●●●              │
│                         │
│  [0] [1] [2] ... [15]   │  ← Servo channels
│   ●    ●    ●       ●   │
└─────────────────────────┘
```

### MG995 Servo Wire Colors

| Wire Color | Function | Connects To |
|------------|----------|-------------|
| Red        | Power    | V+ (5V)     |
| Brown/Black| Ground   | GND         |
| Orange/Yellow | Signal | Channel pin |

## Safety Reminders

⚠️ **Never power servos from Pi's 5V pins**  
⚠️ **Always use common ground**  
⚠️ **Check polarity before connecting power**  
⚠️ **Start with low power and test**  
⚠️ **Have emergency stop ready (power switch)**  

## Support

If you encounter issues:
1. Check this wiring guide
2. Verify each connection systematically
3. Test components individually
4. Check troubleshooting section in README.md
5. Double-check power supply specifications

**Good luck building Ash! 🤖**

