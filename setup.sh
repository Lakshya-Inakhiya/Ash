#!/bin/bash
# Setup script for Ash Robot
# This script helps automate the installation process on Raspberry Pi

set -e  # Exit on error

echo "================================================"
echo "  Ash Robot Setup Script"
echo "================================================"
echo ""

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "Warning: This doesn't appear to be a Raspberry Pi"
    echo "This script is designed for Raspberry Pi OS"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update system
echo "[1/6] Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install system dependencies
echo "[2/6] Installing system dependencies..."
sudo apt-get install -y \
    python3-pip \
    python3-pil \
    i2c-tools \
    portaudio19-dev \
    python3-all-dev \
    git

# Install Python packages
echo "[3/6] Installing Python packages..."
pip3 install -r requirements.txt

# Check if I2C is enabled
echo "[4/6] Checking I2C configuration..."
if ! sudo raspi-config nonint get_i2c | grep -q 0; then
    echo "Enabling I2C interface..."
    sudo raspi-config nonint do_i2c 0
    echo "I2C enabled"
else
    echo "I2C already enabled"
fi

# Check for LCD driver
echo "[5/6] Checking LCD driver..."
if [ ! -d "$HOME/LCD-show" ]; then
    echo "LCD-show driver not found"
    read -p "Install LCD driver now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd ~
        git clone https://github.com/goodtft/LCD-show.git
        chmod -R 755 LCD-show
        echo "LCD driver downloaded to ~/LCD-show"
        echo "Run 'cd ~/LCD-show && sudo ./LCD35-show' to install"
    fi
else
    echo "LCD-show driver found at ~/LCD-show"
fi

# Check for .env file
echo "[6/6] Checking configuration..."
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found"
    echo "You need to create a .env file with your Gemini API key"
    echo ""
    echo "Get your API key from: https://makersuite.google.com/app/apikey"
    echo ""
    read -p "Create .env file now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Enter your Gemini API key:"
        read -r api_key
        echo "GEMINI_API_KEY=$api_key" > .env
        echo ".env file created"
    fi
else
    echo ".env file found"
fi

# Check for face images
echo ""
echo "Checking face images..."
missing_faces=0
for face in happy sad neutral listening speaking thinking error; do
    if [ ! -f "assets/faces/${face}.png" ]; then
        echo "  Missing: ${face}.png"
        missing_faces=$((missing_faces + 1))
    else
        echo "  Found: ${face}.png"
    fi
done

if [ $missing_faces -gt 0 ]; then
    echo ""
    echo "Warning: $missing_faces face image(s) missing"
    echo "Please add 480×320 PNG images to assets/faces/"
fi

# Final check
echo ""
echo "================================================"
echo "  Setup Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Ensure LCD driver is installed (cd ~/LCD-show && sudo ./LCD35-show)"
echo "2. Rotate LCD to landscape (cd ~/LCD-show && sudo ./rotate.sh 90)"
echo "3. Add face images to assets/faces/ (7 PNG files, 480×320)"
echo "4. Verify .env file has your Gemini API key"
echo "5. Connect hardware (servos, PCA9685)"
echo "6. Run: python3 src/main.py"
echo ""
echo "Test components individually:"
echo "  python3 src/face_display.py"
echo "  python3 src/gestures.py"
echo "  python3 src/audio_io.py"
echo "  python3 src/llm_client.py"
echo ""
echo "See README.md for detailed instructions"
echo ""

