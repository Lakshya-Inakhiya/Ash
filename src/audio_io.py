"""
Audio I/O Module for Ash Robot.

This module handles speech-to-text (listening) and text-to-speech (speaking)
functionality using Google's free APIs.

Architecture is designed to work initially with Mac's microphone/speakers
over SSH, but structured to easily migrate to Pi's audio hardware later.

Uses sounddevice instead of pyaudio for better cross-platform compatibility.
"""

import os
import tempfile
import time
import io
import wave
import json
import urllib.request
import urllib.parse
from pathlib import Path
import numpy as np
import sounddevice as sd
from gtts import gTTS
import pygame


class AudioIO:
    """
    Handles audio input (speech recognition) and output (text-to-speech).
    
    This class provides a clean interface for listening to user speech and
    speaking responses back using Google's cloud services.
    """
    
    def __init__(self, config):
        """
        Initialize the audio I/O system.
        
        Args:
            config: Configuration dictionary with audio settings
        """
        self.config = config
        self.timeout = config['audio']['timeout']
        self.phrase_time_limit = config['audio']['phrase_time_limit']
        self.language = config['audio']['language']
        self.tts_slow = config['audio']['tts_slow']
        
        # Initialize pygame mixer for audio playback
        pygame.mixer.init()
        
        # Audio recording settings
        self.sample_rate = 16000  # 16kHz is standard for speech
        self.channels = 1  # Mono
        
        # Microphone availability
        self.microphone_available = False
        self._setup_microphone()
        
        print("Audio I/O initialized")
    
    def _setup_microphone(self):
        """
        Set up the microphone for speech recognition using sounddevice.
        
        This method checks if a microphone is available.
        On Mac development, this will use the Mac's microphone.
        On Pi, this will use the Pi's microphone (USB or onboard).
        """
        try:
            # Check if any input devices are available
            devices = sd.query_devices()
            has_input = any(d['max_input_channels'] > 0 for d in devices if isinstance(d, dict))
            
            if has_input:
                # Test recording a tiny bit of audio
                test_duration = 0.1  # 100ms
                test_audio = sd.rec(
                    int(test_duration * self.sample_rate),
                    samplerate=self.sample_rate,
                    channels=self.channels,
                    dtype='int16'
                )
                sd.wait()
                
                self.microphone_available = True
                print("✓ Microphone ready (using sounddevice)")
                print(f"  Sample rate: {self.sample_rate} Hz")
                print(f"  Default device: {sd.query_devices(kind='input')['name']}")
            else:
                raise Exception("No input devices found")
                
        except Exception as e:
            print(f"Warning: Could not initialize microphone: {e}")
            print("Speech recognition will not work until microphone is available.")
            print("\nOn Mac, you may need to:")
            print("  1. Grant microphone permissions: System Settings → Privacy & Security → Microphone")
            print("  2. Allow Terminal/Python to access microphone")
            print("\n⚠️  Falling back to TEXT INPUT mode - type your questions instead!\n")
            self.microphone_available = False
    
    def listen(self):
        """
        Listen for speech and convert it to text using sounddevice.
        
        This function will:
        1. Record audio via the microphone using sounddevice
        2. Send audio to Google Speech Recognition API
        3. Return the transcribed text
        
        If microphone is not available, falls back to text input.
        
        Returns:
            str: Transcribed text, or empty string if no speech detected or error
        """
        if not self.microphone_available:
            # Fallback to text input when mic not available
            print("\n" + "="*50)
            print("Microphone not available - using text input mode")
            print("="*50)
            try:
                user_input = input("You: ").strip()
                return user_input
            except (KeyboardInterrupt, EOFError):
                return ""
        
        try:
            print("Listening... (speak now)")
            
            # Record audio using sounddevice
            duration = self.phrase_time_limit  # Max recording duration
            recording = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype='int16'
            )
            
            # Wait for recording to finish (or timeout)
            sd.wait()
            
            print("Processing speech...")
            
            # Create WAV file in memory
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, 'wb') as wav_file:
                wav_file.setnchannels(self.channels)
                wav_file.setsampwidth(2)  # 16-bit = 2 bytes
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(recording.tobytes())
            
            # Get WAV data
            wav_data = wav_buffer.getvalue()
            
            # Call Google Speech API directly with WAV (avoids FLAC binary issue on ARM Mac)
            text = self._recognize_google_wav(wav_data)
            
            if text:
                print(f"✓ Recognized: {text}")
                return text
            else:
                print("Could not understand audio")
                return ""
        
        except KeyboardInterrupt:
            print("\nListening interrupted")
            return ""
        
        except Exception as e:
            print(f"Error during speech recognition: {e}")
            import traceback
            traceback.print_exc()
            return ""
    
    def _recognize_google_wav(self, wav_data):
        """
        Send WAV audio directly to Google Speech API.
        This bypasses the FLAC encoder requirement (fixes ARM Mac compatibility).
        
        Args:
            wav_data: Raw WAV file data (bytes)
        
        Returns:
            str: Recognized text, or None if recognition failed
        """
        try:
            # Google Speech API v2 endpoint (free, no key required for limited use)
            url = f"http://www.google.com/speech-api/v2/recognize?client=chromium&lang={self.language}&key=AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw"
            
            # Prepare request
            request = urllib.request.Request(
                url,
                data=wav_data,
                headers={
                    "Content-Type": "audio/l16; rate=16000;"
                }
            )
            
            # Send request
            response = urllib.request.urlopen(request, timeout=10)
            response_text = response.read().decode('utf-8')
            
            # Parse response (multiple JSON objects, one per line)
            for line in response_text.split('\n'):
                if line.strip():
                    try:
                        result = json.loads(line)
                        if 'result' in result and result['result']:
                            alternative = result['result'][0].get('alternative', [])
                            if alternative and 'transcript' in alternative[0]:
                                return alternative[0]['transcript']
                    except json.JSONDecodeError:
                        continue
            
            return None
            
        except urllib.error.HTTPError as e:
            print(f"Speech API HTTP error: {e.code}")
            return None
        except urllib.error.URLError as e:
            print(f"Speech API URL error: {e.reason}")
            return None
        except Exception as e:
            print(f"Speech API error: {e}")
            return None
    
    def speak(self, text):
        """
        Convert text to speech and play it.
        
        This function will:
        1. Convert text to speech using Google TTS
        2. Save audio to a temporary file
        3. Play the audio through speakers
        
        Args:
            text: The text to speak
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not text or not text.strip():
            print("Warning: Empty text provided to speak()")
            return False
        
        try:
            print(f"Speaking: {text}")
            
            # Generate speech using gTTS
            tts = gTTS(text=text, lang=self.language, slow=self.tts_slow)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                temp_file = fp.name
                tts.save(temp_file)
            
            # Play audio using pygame
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            # Clean up temporary file
            try:
                os.unlink(temp_file)
            except:
                pass  # File might still be in use on some systems
            
            return True
            
        except Exception as e:
            print(f"Error during text-to-speech: {e}")
            return False
    
    def test_microphone(self):
        """
        Test the microphone by recording and displaying audio levels.
        Useful for debugging microphone issues.
        """
        if self.microphone is None:
            print("Microphone not available")
            return
        
        print("Testing microphone (speak now)...")
        print("This will record for 5 seconds")
        
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                print("Audio recorded successfully!")
                print(f"Audio data size: {len(audio.frame_data)} bytes")
        except Exception as e:
            print(f"Microphone test failed: {e}")
    
    def close(self):
        """
        Clean up audio resources.
        """
        pygame.mixer.quit()
        print("Audio I/O closed")


# Standalone convenience functions

def listen_once(timeout=5, phrase_limit=10, language="en"):
    """
    Simple function to listen for speech once.
    
    Args:
        timeout: Seconds to wait for speech to start
        phrase_limit: Maximum seconds to record
        language: Language code (e.g., "en")
    
    Returns:
        str: Transcribed text, or empty string on error
    """
    recognizer = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)
            text = recognizer.recognize_google(audio, language=language)
            return text
    except Exception as e:
        print(f"Error: {e}")
        return ""


def speak_once(text, language="en", slow=False):
    """
    Simple function to speak text once.
    
    Args:
        text: Text to speak
        language: Language code (e.g., "en")
        slow: Speak slowly if True
    
    Returns:
        bool: True if successful
    """
    try:
        tts = gTTS(text=text, lang=language, slow=slow)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            temp_file = fp.name
            tts.save(temp_file)
        
        pygame.mixer.init()
        pygame.mixer.music.load(temp_file)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        
        pygame.mixer.quit()
        os.unlink(temp_file)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    """
    Test function for the audio I/O module.
    """
    import sys
    sys.path.append(str(Path(__file__).parent))
    from utils import load_config
    
    print("Audio I/O Test")
    print("-" * 40)
    
    try:
        config = load_config()
        audio = AudioIO(config)
        
        # Test TTS
        print("\n1. Testing Text-to-Speech...")
        audio.speak("Hello! I am Ash, your desktop robot assistant.")
        time.sleep(1)
        
        # Test microphone
        print("\n2. Testing Microphone...")
        audio.test_microphone()
        
        # Test speech recognition
        print("\n3. Testing Speech Recognition...")
        print("Please say something...")
        text = audio.listen()
        
        if text:
            print(f"You said: {text}")
            audio.speak(f"You said: {text}")
        else:
            print("No speech detected")
        
        audio.close()
        print("\nTest complete!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

