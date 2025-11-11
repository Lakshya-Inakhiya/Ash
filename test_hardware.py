#!/usr/bin/env python3
"""
Hardware Testing Script for Ash Robot

This script tests each hardware component individually to help
identify issues before running the full system.

Usage:
    python3 test_hardware.py
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from utils import load_config, load_env


def test_lcd_display():
    """Test LCD display."""
    print("\n" + "="*60)
    print("TEST 1: LCD Display")
    print("="*60)
    
    try:
        from face_display import FaceDisplay
        config = load_config()
        display = FaceDisplay(config)
        
        if display.has_framebuffer:
            print("✅ LCD framebuffer detected: /dev/fb1")
        else:
            print("⚠️  LCD framebuffer not found (simulation mode)")
        
        if display.image_cache:
            print(f"✅ Face images loaded: {len(display.image_cache)} expressions")
            print(f"   Expressions: {list(display.image_cache.keys())}")
        else:
            print("❌ No face images found!")
            return False
        
        print("\nTesting display...")
        display.test_all_expressions(delay=1)
        display.close()
        
        print("\n✅ LCD Display: PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ LCD Display: FAILED")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_i2c_communication():
    """Test I2C communication with PCA9685."""
    print("\n" + "="*60)
    print("TEST 2: I2C Communication (PCA9685)")
    print("="*60)
    
    try:
        import subprocess
        result = subprocess.run(
            ['sudo', 'i2cdetect', '-y', '1'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        output = result.stdout
        print("I2C Bus Scan:")
        print(output)
        
        if '40' in output:
            print("\n✅ PCA9685 detected at address 0x40")
            return True
        else:
            print("\n❌ PCA9685 NOT detected!")
            print("   Check wiring:")
            print("   - VCC → Pi Pin 1 (3.3V)")
            print("   - GND → Pi Pin 6")
            print("   - SDA → Pi Pin 3")
            print("   - SCL → Pi Pin 5")
            print("   - I2C enabled: sudo raspi-config")
            return False
            
    except FileNotFoundError:
        print("\n❌ i2cdetect not found")
        print("   Install: sudo apt-get install i2c-tools")
        return False
    except Exception as e:
        print(f"\n❌ I2C Test: FAILED")
        print(f"   Error: {e}")
        return False


def test_servos():
    """Test servo motors."""
    print("\n" + "="*60)
    print("TEST 3: Servo Motors")
    print("="*60)
    
    try:
        from gestures import ServoController
        config = load_config()
        servos = ServoController(config)
        
        if servos.pca is None:
            print("⚠️  Servos in simulation mode (hardware not detected)")
            print("   This is normal if:")
            print("   - Running on Mac")
            print("   - PCA9685 not connected")
            print("   - I2C not enabled")
            return False
        
        print("✅ Servo controller initialized")
        print(f"   Left arm: Channel {servos.left_arm_channel}")
        print(f"   Right arm: Channel {servos.right_arm_channel}")
        
        print("\n⚠️  WARNING: Servos will move!")
        print("   Make sure:")
        print("   - Servo power supply is ON")
        print("   - Servos are not obstructed")
        print("   - You can stop with Ctrl+C")
        
        response = input("\nProceed with servo test? (y/n): ")
        if response.lower() != 'y':
            print("Skipped servo movement test")
            servos.close()
            return True
        
        print("\nTesting servos (watch carefully)...")
        servos.test_servos()
        servos.close()
        
        print("\n✅ Servos: PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Servos: FAILED")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_audio_input():
    """Test audio input (microphone)."""
    print("\n" + "="*60)
    print("TEST 4: Audio Input (Microphone)")
    print("="*60)
    
    try:
        from audio_io import AudioIO
        config = load_config()
        audio = AudioIO(config)
        
        if audio.microphone_available:
            print("✅ Microphone detected")
            print(f"   Device: {audio.microphone}")
            print(f"   Sample rate: {audio.sample_rate} Hz")
            
            print("\nTesting microphone...")
            print("(This will record for 2 seconds)")
            audio.test_microphone()
            
            print("\n✅ Microphone: PASSED")
            return True
        else:
            print("❌ Microphone not available")
            print("   Check:")
            print("   - USB microphone connected")
            print("   - Permissions granted")
            print("   - Device recognized: arecord -l")
            return False
            
    except Exception as e:
        print(f"\n❌ Audio Input: FAILED")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_audio_output():
    """Test audio output (speaker)."""
    print("\n" + "="*60)
    print("TEST 5: Audio Output (Speaker)")
    print("="*60)
    
    try:
        from audio_io import AudioIO
        config = load_config()
        audio = AudioIO(config)
        
        print("Testing text-to-speech...")
        test_text = "Hello! This is a test of the audio output system."
        result = audio.speak(test_text)
        
        if result:
            print("\n✅ Audio Output: PASSED")
            print("   Did you hear the test message?")
            return True
        else:
            print("\n❌ Audio Output: FAILED")
            print("   Check:")
            print("   - Speaker connected")
            print("   - Volume up")
            print("   - Device recognized: aplay -l")
            return False
            
    except Exception as e:
        print(f"\n❌ Audio Output: FAILED")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_gemini_api():
    """Test Gemini API."""
    print("\n" + "="*60)
    print("TEST 6: Gemini API")
    print("="*60)
    
    try:
        from llm_client import LLMClient
        from utils import get_api_key
        
        load_env()
        config = load_config()
        api_key = get_api_key()
        
        client = LLMClient(config, api_key)
        
        print("Testing Gemini API...")
        test_question = "Say hello in one sentence."
        response = client.ask(test_question)
        
        print(f"\nQuestion: {test_question}")
        print(f"Response: {response}")
        
        if response and len(response) > 0:
            print("\n✅ Gemini API: PASSED")
            return True
        else:
            print("\n❌ Gemini API: FAILED")
            print("   No response received")
            return False
            
    except ValueError as e:
        print(f"\n❌ Gemini API: FAILED")
        print(f"   {e}")
        print("   Check .env file has GEMINI_API_KEY")
        return False
    except Exception as e:
        print(f"\n❌ Gemini API: FAILED")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all hardware tests."""
    print("╔" + "="*58 + "╗")
    print("║" + " "*10 + "ASH ROBOT - HARDWARE TEST SUITE" + " "*15 + "║")
    print("╚" + "="*58 + "╝")
    
    print("\nThis script will test each hardware component individually.")
    print("Run tests in order to identify any issues.\n")
    
    results = {}
    
    # Test 1: LCD Display
    results['LCD'] = test_lcd_display()
    time.sleep(1)
    
    # Test 2: I2C Communication
    results['I2C'] = test_i2c_communication()
    time.sleep(1)
    
    # Test 3: Servos (optional, requires power)
    results['Servos'] = test_servos()
    time.sleep(1)
    
    # Test 4: Audio Input
    results['Microphone'] = test_audio_input()
    time.sleep(1)
    
    # Test 5: Audio Output
    results['Speaker'] = test_audio_output()
    time.sleep(1)
    
    # Test 6: Gemini API
    results['Gemini'] = test_gemini_api()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for component, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{component:15} {status}")
    
    total = len(results)
    passed = sum(results.values())
    
    print("\n" + "="*60)
    print(f"Results: {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print("\n🎉 All tests passed! Hardware is ready!")
        print("You can now run: python3 src/main.py")
    else:
        print("\n⚠️  Some tests failed. Review errors above.")
        print("Fix issues before running full system.")
    
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(0)

