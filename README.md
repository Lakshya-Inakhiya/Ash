# Ash - Desktop AI Robot

Ash is a desktop AI robot built with Raspberry Pi 5 that features:
- Animated facial expressions on a 3.5" LCD screen
- Voice interaction (speech-to-text and text-to-speech)
- AI-powered responses using Google Gemini
- Expressive servo-controlled arm gestures

## Table of Contents

- [Hardware Requirements](#hardware-requirements)
- [Software Requirements](#software-requirements)
- [Hardware Setup & Wiring](#hardware-setup--wiring)
- [Software Installation](#software-installation)
- [Configuration](#configuration)
- [Creating Face Images](#creating-face-images)
- [Running Ash](#running-ash)
- [Testing Individual Components](#testing-individual-components)
- [Troubleshooting](#troubleshooting)
- [Project Structure](#project-structure)
- [Future Enhancements](#future-enhancements)

## Hardware Requirements

### Core Components
- **Raspberry Pi 5** (4GB RAM recommended)
- **3.5" LCD Display** (320x480, ILI9486 driver, SPI interface)
  - Model: MPI3501 or compatible
  - Link: https://www.lcdwiki.com/3.5inch_RPi_Display
- **PCA9685 16-Channel PWM Servo Driver Board**
- **2× MG995 Servo Motors** (for arm movements)
- **MicroSD Card** (32GB+, Class 10)

### Power Supply
- **Raspberry Pi**: Official 5V 3A USB-C power adapter
- **Servos**: Separate 5V 2A+ power supply (minimum 2A, 3A recommended)
  - **CRITICAL**: Do NOT power servos from Pi's 5V rail!

### Accessories
- Jumper wires (male-to-female)
- Breadboard (optional, for prototyping)
- USB microphone and speaker (for initial development)

## Software Requirements

### Operating System
- Raspberry Pi OS (64-bit recommended)
- Tested on: Raspberry Pi OS Bookworm

### Python Version
- Python 3.9 or higher

## Hardware Setup & Wiring

### 1. LCD Display Connection

The 3.5" LCD plugs directly into the Raspberry Pi GPIO header:

```
LCD Module → Raspberry Pi GPIO Pins 1-26
(Plugs directly onto first 26 pins of GPIO header)
```

**Important Notes:**
- The LCD covers pins 1-26, but internal connections only use specific pins
- Other GPIO pins (27-40) remain available for other components
- The LCD uses SPI interface and creates `/dev/fb1` framebuffer device

### 2. PCA9685 Servo Driver Wiring

**PCA9685 to Raspberry Pi 5:**

```
PCA9685 Pin    →  Raspberry Pi Pin     (GPIO)
----------------------------------------
VCC            →  Pin 1                (3.3V)
GND            →  Pin 6                (GND)
SDA            →  Pin 3                (GPIO 2 / SDA)
SCL            →  Pin 5                (GPIO 3 / SCL)
```

**PCA9685 to Servo Power Supply:**

```
PCA9685 Pin    →  5V Power Supply
----------------------------------------
V+             →  5V (+)
GND            →  GND (-) **AND** Raspberry Pi GND (common ground!)
```

⚠️ **CRITICAL**: The servo power supply GND **MUST** connect to both:
- PCA9685 GND
- Raspberry Pi GND (Pin 6 or any other GND pin)

This creates a common ground, which is essential for proper servo control.

**Servos to PCA9685:**

```
Servo          →  PCA9685 Channel
----------------------------------------
Left Arm       →  Channel 0 (signal wire)
Right Arm      →  Channel 1 (signal wire)

Each servo also connects:
- Red wire    → Servo power supply 5V+
- Brown/Black → Servo power supply GND
- Orange/Yellow (signal) → PCA9685 channel
```

### Wiring Diagram (Text Format)

```
                    ┌─────────────────┐
                    │  Raspberry Pi 5 │
                    │                 │
      ┌─────────────┤ Pin 1-26        │
      │ LCD Display │                 │
      └─────────────┤                 │
                    │  Pin 3 (SDA) ───┼─────┐
                    │  Pin 5 (SCL) ───┼───┐ │
                    │  Pin 6 (GND) ───┼─┐ │ │
                    └─────────────────┘ │ │ │
                                        │ │ │
                    ┌───────────────────┘ │ │
                    │ ┌───────────────────┘ │
                    │ │ ┌───────────────────┘
                    │ │ │
                ┌───┴─┴─┴────┐
                │   PCA9685  │
                │  (Servo    │
                │   Driver)  │
                │            │
                │ V+ ────────┼─────── 5V Power Supply (+)
                │ GND ───────┼─┐
                └────────────┘ │
                    │ │        │
                    │ └────────┼─────── 5V Power Supply (-)
                    │          │         AND Pi GND (common ground)
                 Channel 0     │
                    │       Channel 1
                    │          │
                ┌───┴───┐  ┌───┴───┐
                │ Left  │  │ Right │
                │ Servo │  │ Servo │
                │(MG995)│  │(MG995)│
                └───────┘  └───────┘
                 (Red wires to 5V+, Black to GND)
```

### Safety Notes

⚠️ **IMPORTANT SAFETY INFORMATION**

1. **Never connect servos to Pi's 5V rail** - MG995 servos can draw 1A+ each under load, which exceeds the Pi's 5V rail capacity
2. **Always use common ground** - Connect servo power supply GND to both PCA9685 and Pi GND
3. **Check polarity** - Double-check all power connections before powering on
4. **Start with neutral position** - Always initialize servos to neutral (90°) to avoid sudden movements
5. **Monitor temperature** - LCD draws ~130mA; if Pi gets hot, ensure adequate cooling
6. **Use quality power supplies** - Cheap supplies can cause servo jitter and Pi instability

## Software Installation

### 1. Raspberry Pi OS Setup

Flash Raspberry Pi OS to your SD card using Raspberry Pi Imager:
- Download: https://www.raspberrypi.com/software/

### 2. Initial System Configuration

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Enable I2C interface (required for PCA9685)
sudo raspi-config
# Navigate to: Interface Options → I2C → Enable
# Reboot when prompted

# Verify I2C is enabled
sudo i2cdetect -y 1
# Should show a device at address 0x40 (PCA9685)
```

### 3. Install LCD Driver

```bash
# Install LCD-show driver for 3.5" display
cd ~
sudo rm -rf LCD-show
git clone https://github.com/goodtft/LCD-show.git
chmod -R 755 LCD-show
cd LCD-show/

# Install driver and reboot
sudo ./LCD35-show

# After reboot, rotate to landscape mode
cd ~/LCD-show/
sudo ./rotate.sh 90
```

The display should now work in 480×320 landscape mode.

### 4. Install System Dependencies

```bash
sudo apt-get install -y \
    python3-pip \
    python3-pil \
    i2c-tools \
    portaudio19-dev \
    python3-pyaudio \
    git
```

### 5. Install Python Dependencies

```bash
# Clone or navigate to the Ash-1 project directory
cd ~/Desktop/Ash-1

# Install Python packages
pip3 install -r requirements.txt
```

**Note**: If you encounter issues with `pyaudio`, try:
```bash
sudo apt-get install portaudio19-dev python3-all-dev
pip3 install pyaudio
```

## Configuration

### 1. Get Gemini API Key

1. Visit: https://makersuite.google.com/app/apikey
2. Create a new API key
3. Copy the key

### 2. Create .env File

Create a `.env` file in the project root:

```bash
cd ~/Desktop/Ash-1
nano .env
```

Add your API key:

```env
GEMINI_API_KEY=your_actual_api_key_here
```

Save and exit (Ctrl+X, Y, Enter).

### 3. Adjust Settings (Optional)

Edit `config/settings.yaml` to customize:
- Servo angles and speeds
- Audio timeouts
- Cooldown periods
- Display settings

## Creating Face Images

Ash requires 7 face images (480×320 pixels each) in PNG format:

1. **happy.png** - Displayed after giving an answer
2. **sad.png** - For empathetic responses
3. **neutral.png** - Default/idle expression
4. **listening.png** - While listening for speech
5. **speaking.png** - While speaking a response
6. **thinking.png** - While processing with Gemini AI
7. **error.png** - When an error occurs

### Creating the Images

You can create these images using:
- Image editing software (Photoshop, GIMP, etc.)
- AI image generators (DALL-E, Midjourney, Stable Diffusion)
- Simple drawings or emoji-based designs

**Requirements:**
- Resolution: 480×320 pixels
- Format: PNG
- Location: `assets/faces/` directory

**Example prompt for AI image generator:**
```
"Simple cartoon robot face, friendly expression, happy/sad/neutral/etc.,
 480×320 pixels, minimalist design, suitable for small LCD screen"
```

### Placing the Images

```bash
cd ~/Desktop/Ash-1
# Copy your PNG files to:
cp /path/to/your/images/*.png assets/faces/

# Verify all 7 images are present:
ls -l assets/faces/
```

## Running Ash

### Start Ash Robot

```bash
cd ~/Desktop/Ash-1
python3 src/main.py
```

### What to Expect

1. **Initialization**: Ash will initialize all components (~5-10 seconds)
2. **Startup Sequence**: Displays happy face, waves, and says "Hello!"
3. **Listening Loop**: Shows listening face and waits for your speech
4. **Interaction**: When you speak:
   - Transcribes your speech
   - Shows thinking face and points
   - Calls Gemini API
   - Shows speaking face and responds
   - Shows happy face and raises arms
   - Waits 3 seconds (cooldown) before listening again

### Stopping Ash

Press `Ctrl+C` to stop. Ash will perform a graceful shutdown:
- Say goodbye
- Return servos to neutral position
- Clear the display
- Close all resources

## Testing Individual Components

Each module can be tested independently:

### Test Face Display

```bash
python3 src/face_display.py
```

This will cycle through all face expressions (if images are present).

### Test Servos

```bash
python3 src/gestures.py
```

Tests all gesture functions and optionally performs a full range test.

### Test Audio

```bash
python3 src/audio_io.py
```

Tests text-to-speech and speech recognition.

### Test Gemini API

```bash
python3 src/llm_client.py
```

Sends test questions to Gemini and displays responses.

## Troubleshooting

### Display Issues

**Problem**: Display shows nothing or distorted image
- **Solution**: 
  ```bash
  cd ~/LCD-show
  sudo ./LCD35-show
  sudo reboot
  ```

**Problem**: Display is rotated wrong way
- **Solution**:
  ```bash
  cd ~/LCD-show
  sudo ./rotate.sh 90  # or 0, 180, 270
  ```

### Servo Issues

**Problem**: Servos not moving
- Check PCA9685 is detected: `sudo i2cdetect -y 1` (should show 0x40)
- Verify I2C is enabled in `raspi-config`
- Check servo power supply is connected and powered on
- Verify common ground between Pi and servo power supply

**Problem**: Servos jittering or behaving erratically
- Check power supply voltage (should be stable 5V)
- Ensure power supply provides sufficient current (2A minimum)
- Verify all ground connections
- Check for loose wires

**Problem**: Error: "No module named 'board'"
- Install CircuitPython libraries:
  ```bash
  pip3 install adafruit-circuitpython-pca9685 adafruit-circuitpython-motor
  ```

### Audio Issues

**Problem**: No microphone detected
- Check USB microphone is connected
- List audio devices: `arecord -l`
- Test microphone: `arecord -d 5 test.wav`

**Problem**: No sound output
- Check speaker volume
- Test speaker: `speaker-test -t wav`

**Problem**: "No module named 'pyaudio'"
- Install dependencies:
  ```bash
  sudo apt-get install portaudio19-dev python3-all-dev
  pip3 install pyaudio
  ```

### Gemini API Issues

**Problem**: "GEMINI_API_KEY not set"
- Create `.env` file in project root
- Add: `GEMINI_API_KEY=your_key_here`
- Verify file is saved

**Problem**: API rate limit errors
- Wait a few minutes between calls
- Free tier has limits; consider upgrading if needed

### General Issues

**Problem**: "Permission denied" errors
- Add user to I2C group: `sudo usermod -a -G i2c $USER`
- Add user to audio group: `sudo usermod -a -G audio $USER`
- Log out and back in

**Problem**: Module import errors
- Verify you're in correct directory: `cd ~/Desktop/Ash-1`
- Reinstall requirements: `pip3 install -r requirements.txt`

## Project Structure

```
Ash-1/
├── config/
│   └── settings.yaml          # Configuration file
├── src/
│   ├── main.py                # Main entry point
│   ├── face_display.py        # LCD face rendering
│   ├── llm_client.py          # Gemini API wrapper
│   ├── audio_io.py            # Speech I/O
│   ├── gestures.py            # Servo control
│   └── utils.py               # Helper functions
├── assets/
│   └── faces/                 # Face images (7 PNGs)
│       ├── happy.png
│       ├── sad.png
│       ├── neutral.png
│       ├── listening.png
│       ├── speaking.png
│       ├── thinking.png
│       └── error.png
├── requirements.txt           # Python dependencies
├── .env                       # API keys (not in git)
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## Development Notes

### Developing on Mac

The code is structured to work in "simulation mode" when hardware is not available:

- **Face Display**: Shows debug messages instead of writing to framebuffer
- **Servos**: Prints movement commands instead of controlling hardware
- **Audio**: Uses Mac's microphone and speakers

This allows you to develop and test the interaction logic before deploying to the Pi.

### Deploying to Pi

1. Copy project to Pi:
   ```bash
   scp -r Ash-1 pi@raspberrypi.local:~/Desktop/
   ```

2. SSH into Pi and run:
   ```bash
   ssh pi@raspberrypi.local
   cd ~/Desktop/Ash-1
   python3 src/main.py
   ```

## Future Enhancements

Ideas for extending Ash:

- **Wake Word Detection**: Use Porcupine or similar for "Hey Ash" activation
- **Voice Activity Detection**: Better start/stop detection for natural conversation
- **Camera Integration**: Add Pi Camera for visual perception
- **More Gestures**: Expand servo choreography
- **Local LLM**: Run Ollama on Pi 5 for offline operation
- **Multiple Servos**: Add more degrees of freedom
- **Custom Voice**: Use ElevenLabs or other premium TTS
- **Emotion Detection**: Analyze user sentiment and respond appropriately
- **Memory/Context**: Add conversation history and personalization
- **Web Interface**: Control and monitor via web dashboard

## Credits

- **LCD Driver**: goodtft/LCD-show (https://github.com/goodtft/LCD-show)
- **Servo Control**: Adafruit CircuitPython libraries
- **AI**: Google Gemini API
- **TTS**: Google Text-to-Speech (gTTS)
- **STT**: Google Speech Recognition

## License

This project is open source and available for personal and educational use.

## Support

For issues, questions, or contributions:
- Check the [Troubleshooting](#troubleshooting) section
- Review component documentation
- Test modules individually to isolate problems

## Safety Warning

This project involves electronics and moving parts. Please:
- Double-check all wiring before powering on
- Use proper power supplies
- Keep servo arms clear of obstructions
- Supervise operation
- Follow electrical safety guidelines

**Enjoy building and interacting with Ash!** 🤖

