#!/bin/bash
# Set up Ash on Raspberry Pi OS (Bookworm or newer). Safe to re-run.
set -euo pipefail
cd "$(dirname "$0")/.."  # repo root

echo "Installing system packages..."
sudo apt-get update
sudo apt-get install -y python3-venv python3-dev build-essential libportaudio2 i2c-tools

if command -v raspi-config >/dev/null; then
    echo "Enabling I2C and SPI..."
    sudo raspi-config nonint do_i2c 0
    sudo raspi-config nonint do_spi 0
    sudo usermod -aG gpio,i2c,spi,audio "$USER"
fi

echo "Creating virtual environment..."
python3 -m venv venv
venv/bin/pip install --upgrade pip
venv/bin/pip install -r hardware/requirements.txt

if [ ! -f .env ]; then
    read -rsp "Groq API key (from https://console.groq.com/keys, blank to skip): " key
    echo
    if [ -n "$key" ]; then
        (umask 077 && echo "GROQ_API_KEY=$key" > .env)
    else
        cp .env.example .env && chmod 600 .env
        echo "Edit .env and add your key before running Ash."
    fi
fi

echo
echo "Done. If this is the first run, reboot so I2C/SPI and group changes apply."
echo "Then start Ash with: venv/bin/python -m hardware.main"
