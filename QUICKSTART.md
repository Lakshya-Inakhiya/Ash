# Quick Start Guide for Ash Robot

This is a condensed guide to get Ash up and running quickly. For detailed information, see [README.md](README.md).

## Prerequisites Checklist

- [ ] Raspberry Pi 5 with Raspberry Pi OS installed
- [ ] 3.5" LCD display plugged into GPIO pins 1-26
- [ ] PCA9685 connected to Pi (I2C pins 3 & 5)
- [ ] 2× MG995 servos connected to PCA9685 channels 0 & 1
- [ ] Separate 5V 2A+ power supply for servos
- [ ] Common ground between Pi and servo power supply
- [ ] USB microphone and speaker
- [ ] Internet connection (for Gemini API)

## Fast Setup (5 Steps)

### 1. Install LCD Driver

```bash
cd ~
git clone https://github.com/goodtft/LCD-show.git
cd LCD-show
sudo ./LCD35-show
# System will reboot

# After reboot, rotate to landscape:
cd ~/LCD-show
sudo ./rotate.sh 90
```

### 2. Enable I2C

```bash
sudo raspi-config
# Navigate to: Interface Options → I2C → Enable
sudo reboot
```

### 3. Install Dependencies

```bash
cd ~/Desktop/Ash-1
sudo apt-get update
sudo apt-get install -y python3-pip python3-pil i2c-tools portaudio19-dev
pip3 install -r requirements.txt
```

### 4. Configure API Key

Get API key from: https://makersuite.google.com/app/apikey

```bash
cd ~/Desktop/Ash-1
nano .env
```

Add:
```
GEMINI_API_KEY=your_actual_api_key_here
```

Save (Ctrl+X, Y, Enter).

### 5. Add Face Images

Place 7 PNG images (480×320) in `assets/faces/`:
- happy.png
- sad.png
- neutral.png
- listening.png
- speaking.png
- thinking.png
- error.png

## Run Ash

```bash
cd ~/Desktop/Ash-1
python3 src/main.py
```

## Test Individual Components

```bash
# Test display
python3 src/face_display.py

# Test servos
python3 src/gestures.py

# Test audio
python3 src/audio_io.py

# Test Gemini API
python3 src/llm_client.py
```

## Common Issues

**Servos not moving?**
```bash
sudo i2cdetect -y 1  # Should show 0x40
```

**No microphone?**
```bash
arecord -l  # List audio devices
```

**API key error?**
- Check `.env` file exists and has correct key
- Verify file is in project root (`~/Desktop/Ash-1/.env`)

## Next Steps

1. Test each component individually
2. Verify all 7 face images are present
3. Run main.py and start talking to Ash!

See [README.md](README.md) for complete documentation.

