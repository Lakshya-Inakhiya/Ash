#!/bin/bash
# Fix LCD Driver Installation Script
# This script fixes the LCD driver installation when network issues prevented cmake installation

set -e

echo "=========================================="
echo "LCD Driver Installation Fix"
echo "=========================================="
echo ""

# Check if running on Pi (should have /etc/rpi-issue)
if [ ! -f /etc/rpi-issue ]; then
    echo "Warning: This script should be run on a Raspberry Pi"
    echo "Press Ctrl+C to cancel, or Enter to continue..."
    read
fi

# Step 1: Update package list
echo "Step 1: Updating package list..."
sudo apt-get update

# Step 2: Install required dependencies manually
echo ""
echo "Step 2: Installing required dependencies..."
sudo apt-get install -y \
    cmake \
    build-essential \
    git \
    xserver-xorg-input-evdev \
    python3 \
    python3-pip

# Step 3: Check if LCD-show directory exists
echo ""
echo "Step 3: Checking LCD-show directory..."
if [ ! -d ~/LCD-show ]; then
    echo "LCD-show directory not found. Cloning from GitHub..."
    cd ~
    git clone https://github.com/goodtft/LCD-show.git
    chmod -R 755 LCD-show
else
    echo "LCD-show directory found."
fi

# Step 4: Navigate to LCD-show directory
cd ~/LCD-show

# Step 5: Make sure scripts are executable
echo ""
echo "Step 4: Making scripts executable..."
chmod +x *.sh

# Step 6: Check network connectivity
echo ""
echo "Step 5: Checking network connectivity..."
if ping -c 1 google.com &> /dev/null; then
    echo "Network is working. Proceeding with installation..."
else
    echo "Warning: Network connectivity issues detected!"
    echo "Some features may not work properly."
    echo "Press Enter to continue anyway, or Ctrl+C to cancel..."
    read
fi

# Step 7: Run LCD35-show installation
echo ""
echo "Step 6: Running LCD35-show installation..."
echo "This will install the LCD driver and reboot the system."
echo "Press Enter to continue, or Ctrl+C to cancel..."
read

sudo ./LCD35-show

# Note: Script will reboot after this, so we won't reach here
echo ""
echo "Installation started. System will reboot shortly..."
echo "After reboot, SSH back in and run:"
echo "  cd ~/LCD-show"
echo "  sudo ./rotate.sh 90"
echo "  sudo reboot"

