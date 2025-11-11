# Ash Robot - Hardware Deployment Checklist

Quick reference checklist for hardware deployment. Use this alongside `HARDWARE_DEPLOYMENT_PLAN.md`.

## 📦 Pre-Deployment

### Hardware Ready?
- [ ] Raspberry Pi 5
- [ ] 3.5" LCD Display (MPI3501)
- [ ] PCA9685 Servo Driver
- [ ] 2× MG995 Servos
- [ ] 5V 2A+ Power Supply (servos)
- [ ] Pi 5 Power Supply (USB-C)
- [ ] USB Microphone
- [ ] USB Speaker
- [ ] Jumper Wires (F-F)
- [ ] MicroSD Card (32GB+)

### Software Ready?
- [ ] Raspberry Pi OS on SD card
- [ ] Pi booted and accessible
- [ ] Internet connection
- [ ] Gemini API key
- [ ] Face images (7 PNGs)

---

## 🔌 Wiring Checklist (NO POWER YET!)

### LCD Display
- [ ] LCD aligned with Pi GPIO pins 1-26
- [ ] Fully seated, flush against board
- [ ] No bent pins

### PCA9685 to Pi
- [ ] VCC → Pi Pin 1 (3.3V)
- [ ] GND → Pi Pin 6
- [ ] SDA → Pi Pin 3
- [ ] SCL → Pi Pin 5

### Servo Power Supply
- [ ] Power (+) → PCA9685 V+
- [ ] Power (-) → PCA9685 GND
- [ ] Power (-) → Pi GND ⚠️ **COMMON GROUND!**
- [ ] Power supply is OFF

### Servos
- [ ] Left servo → Channel 0
- [ ] Right servo → Channel 1
- [ ] Connectors fully seated
- [ ] Correct orientation (signal wire inside)

### Audio
- [ ] USB microphone connected
- [ ] USB speaker connected

---

## 💻 Software Setup

### Pi OS
- [ ] Pi booted successfully
- [ ] SSH access working
- [ ] System updated: `sudo apt-get update && sudo apt-get upgrade`

### LCD Driver
- [ ] LCD-show installed: `cd ~/LCD-show && sudo ./LCD35-show`
- [ ] System rebooted
- [ ] Rotated to landscape: `sudo ./rotate.sh 90`
- [ ] LCD displays desktop

### I2C
- [ ] I2C enabled: `sudo raspi-config` → Interface Options → I2C
- [ ] Rebooted after enabling
- [ ] PCA9685 detected: `sudo i2cdetect -y 1` shows `40`

### Code Deployment
- [ ] Code on Pi (cloned or transferred)
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] .env file created with API key
- [ ] Face images present (7 PNGs)

---

## 🧪 Component Testing

### LCD Display
```bash
python3 src/face_display.py
```
- [ ] All 7 expressions display
- [ ] Images clear and correct size
- [ ] No errors

### I2C Communication
```bash
sudo i2cdetect -y 1
```
- [ ] Shows `40` (PCA9685 detected)

### Servos (Power ON Now!)
```bash
python3 src/gestures.py
```
- [ ] Servos move smoothly
- [ ] All 5 gestures work
- [ ] No jittering
- [ ] Return to neutral

### Microphone
```bash
python3 src/audio_io.py
```
- [ ] Microphone detected
- [ ] Test recording works

### Speaker
```bash
python3 src/audio_io.py
```
- [ ] TTS plays clearly
- [ ] Volume appropriate

### Gemini API
```bash
python3 src/llm_client.py
```
- [ ] API key loaded
- [ ] Test questions answered
- [ ] Responses received

---

## 🎯 Integration Testing

### Face + Servos
```bash
python3 src/main.py --text
```
- [ ] Type: `gestures`
- [ ] Face changes expressions
- [ ] Servos move in sync

### Voice Input
```bash
python3 src/main.py
```
- [ ] Speak: "Hello"
- [ ] Voice recognized
- [ ] Gesture triggered (wave)

### Intelligent Gestures
```bash
python3 src/main.py --text
```
- [ ] Type: `hello` → Wave
- [ ] Type: `who are you` → Point
- [ ] Type: `greet sunil sir` → Wave
- [ ] Type: `that's awesome` → Arms Up

### Full System
```bash
python3 src/main.py --text
```
- [ ] Complete conversation works
- [ ] All gestures trigger correctly
- [ ] TTS plays responses
- [ ] Clean exit works

---

## ⚠️ Safety Checks

### Before Power On
- [ ] All connections double-checked
- [ ] No short circuits
- [ ] Wires not touching
- [ ] Servo power supply OFF
- [ ] Common ground connected

### During Testing
- [ ] Watch servos carefully
- [ ] Stop if servos bind
- [ ] Monitor power supply
- [ ] Check for overheating

### Power Supply
- [ ] Servos use SEPARATE 5V supply
- [ ] NOT using Pi's 5V rail
- [ ] Common ground connected
- [ ] Polarity correct

---

## 🚀 Quick Test Command

Run comprehensive hardware test:

```bash
python3 test_hardware.py
```

This tests all components automatically!

---

## ✅ Ready When:

- [ ] All individual components test successfully
- [ ] Face displays on LCD
- [ ] Servos move smoothly
- [ ] Voice input works
- [ ] TTS plays clearly
- [ ] Gemini API responds
- [ ] Intelligent gestures work
- [ ] Full conversation loop works
- [ ] Clean exit works

---

## 📞 If Issues:

1. Check `HARDWARE_DEPLOYMENT_PLAN.md` for detailed steps
2. Review `HARDWARE_WIRING.md` for wiring diagrams
3. Run `python3 test_hardware.py` to identify issues
4. Check `README.md` troubleshooting section
5. Verify each component individually

---

**Good luck with deployment! 🤖**

