#!/usr/bin/env python3
"""
Main module for Ash Desktop AI Robot.

This is the entry point that brings together all components:
- Face display (LCD)
- Speech recognition and synthesis
- Gemini AI
- Servo gestures

Run this to start Ash's interactive loop.

Usage:
    python3 src/main.py           # Voice mode (default)
    python3 src/main.py --text    # Text-only mode
    python3 src/main.py --help    # Show help
"""

import sys
import time
import signal
import argparse
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent))

from face_display import FaceDisplay
from llm_client import LLMClient
from audio_io import AudioIO
from gestures import ServoController
from utils import load_config, load_env, get_api_key


class AshRobot:
    """
    Main class for Ash robot.
    
    This class orchestrates all components and manages the interaction loop.
    """
    
    def __init__(self, text_mode=False):
        """
        Initialize Ash robot with all components.
        
        Args:
            text_mode: If True, force text-only input mode
        """
        self.force_text_mode = text_mode
        print("=" * 50)
        print("    Initializing Ash Robot")
        print("=" * 50)
        
        # Load configuration
        print("\n[1/5] Loading configuration...")
        self.config = load_config()
        load_env()
        
        # Initialize display
        print("\n[2/5] Initializing face display...")
        self.display = FaceDisplay(self.config)
        
        # Initialize servos
        print("\n[3/5] Initializing servo controller...")
        self.servos = ServoController(self.config)
        
        # Initialize audio
        print("\n[4/5] Initializing audio I/O...")
        self.audio = AudioIO(self.config)
        
        # Initialize LLM client
        print("\n[5/5] Initializing Gemini AI...")
        try:
            api_key = get_api_key()
            self.llm = LLMClient(self.config, api_key)
        except ValueError as e:
            print(f"Error: {e}")
            print("\nPlease create a .env file in the project root with:")
            print("  GEMINI_API_KEY=your_actual_api_key_here")
            print("\nGet your API key from: https://makersuite.google.com/app/apikey")
            sys.exit(1)
        
        # Get settings
        self.cooldown = self.config['main']['cooldown_period']
        self.startup_expression = self.config['main']['startup_expression']
        
        # Running flag
        self.running = False
        
        print("\n" + "=" * 50)
        print("    Ash Robot Ready!")
        print("=" * 50)
    
    def startup_sequence(self):
        """
        Perform startup sequence with face and gestures.
        """
        print("\nPerforming startup sequence...")
        
        # Start with neutral expression and position
        self.display.set_expression(self.startup_expression)
        self.servos.neutral()
        time.sleep(1)
        
        # Greet the user
        self.display.set_expression("happy")
        self.servos.wave(repetitions=2)
        self.audio.speak("Hello! I am Ash. I am ready to assist you.")
        
        time.sleep(1)
    
    def _analyze_gesture_from_input(self, user_input):
        """
        Analyze user input to determine appropriate gesture.
        
        Args:
            user_input: The user's question/statement
            
        Returns:
            tuple: (gesture_function, gesture_name) or (None, None)
        """
        text = user_input.lower()
        
        # Greeting keywords → Wave
        greeting_words = ['hello', 'hi', 'hey', 'greet', 'wave', 'say hello', 'say hi']
        if any(word in text for word in greeting_words):
            return (self.servos.wave, "Wave")
        
        # Celebration/excitement keywords → Arms Up
        celebration_words = ['yay', 'awesome', 'great', 'celebrate', 'congratulations', 
                           'congrats', 'hooray', 'excellent', 'amazing', 'fantastic']
        if any(word in text for word in celebration_words):
            return (self.servos.arms_up, "Arms Up")
        
        # Question keywords → Point (explaining)
        question_words = ['what', 'why', 'how', 'when', 'where', 'who', 'explain', 'tell me']
        if any(text.startswith(word) for word in question_words) or '?' in text:
            return (self.servos.point, "Point")
        
        # Default: no specific gesture (use normal flow)
        return (None, None)
    
    def _demo_gestures(self):
        """
        Demonstrate all available gestures.
        """
        gestures = [
            ("Neutral", self.servos.neutral, "neutral"),
            ("Arms Up", self.servos.arms_up, "happy"),
            ("Arms Down", self.servos.arms_down, "neutral"),
            ("Point", self.servos.point, "thinking"),
            ("Wave", self.servos.wave, "happy"),
        ]
        
        for name, gesture_func, face in gestures:
            print(f"\n→ {name}")
            self.display.set_expression(face)
            gesture_func()
            time.sleep(1.5)
        
        # Return to neutral
        self.display.set_expression("happy")
        self.servos.neutral()
        print("\n" + "="*50)
        print("Gesture demo complete!")
        print("="*50)
    
    def shutdown_sequence(self):
        """
        Perform shutdown sequence gracefully.
        """
        print("\nPerforming shutdown sequence...")
        
        self.display.set_expression("neutral")
        self.audio.speak("Goodbye!")
        
        time.sleep(1)
        
        # Clean up all components
        self.servos.reset()
        self.display.clear()
        
        # Close resources
        self.servos.close()
        self.audio.close()
        self.display.close()
        
        print("\nAsh robot shut down successfully")
    
    def interaction_loop(self):
        """
        Main interaction loop.
        
        This is the core conversation loop that:
        1. Listens for user speech or text input
        2. Processes with Gemini
        3. Responds with speech and gestures
        """
        print("\n" + "=" * 50)
        print("    Starting Interaction Loop")
        print("=" * 50)
        print("\n💡 Tips:")
        print("  • Speak or type your questions")
        print("  • Type 'quit', 'exit', or 'bye' to exit")
        print("  • Type 'gestures' or 'demo' to see all gestures")
        print("  • Type 'text' to switch to text-only mode")
        print("  • Type 'voice' to switch back to voice mode")
        print("  • Press Ctrl+C to exit")
        print("=" * 50 + "\n")
        
        self.running = True
        # Use text mode if forced or if microphone not available
        use_voice = (not self.force_text_mode) and self.audio.microphone_available
        
        while self.running:
            try:
                # Step 1: Listen for user input (voice or text)
                self.display.set_expression("listening")
                self.servos.neutral()
                
                # Choose input method
                if use_voice:
                    print("\n[Listening...] (or press Ctrl+C then type 'text' for text mode)")
                    user_input = self.audio.listen()
                else:
                    print("\n[Text Input Mode]")
                    print("="*50)
                    try:
                        user_input = input("You: ").strip()
                    except (KeyboardInterrupt, EOFError):
                        print("\n\nExiting...")
                        self.running = False
                        break
                
                # Check if we got any input
                if not user_input or not user_input.strip():
                    # No input detected, continue listening
                    continue
                
                # Check for mode switching commands
                user_input_lower = user_input.lower().strip()
                if user_input_lower == "text":
                    use_voice = False
                    print("✓ Switched to TEXT INPUT mode")
                    continue
                elif user_input_lower == "voice":
                    if self.audio.microphone_available:
                        use_voice = True
                        print("✓ Switched to VOICE INPUT mode")
                    else:
                        print("✗ Microphone not available, staying in text mode")
                    continue
                
                # Check for quit commands
                if user_input_lower in ["quit", "exit", "bye", "goodbye", "stop"]:
                    print(f"\nUser: {user_input}")
                    print("Ash: Goodbye! Have a great day!")
                    self.display.set_expression("happy")
                    self.audio.speak("Goodbye! Have a great day!")
                    self.running = False
                    break
                
                # Check for gesture demo command
                if user_input_lower in ["gestures", "demo", "show gestures", "test gestures", "demo gestures"]:
                    print(f"\nUser: {user_input}")
                    print("\n" + "="*50)
                    print("    Gesture Demo - Watch the servo positions!")
                    print("="*50)
                    self._demo_gestures()
                    continue
                
                print(f"User: {user_input}")
                
                # Analyze input for appropriate gestures
                special_gesture, gesture_name = self._analyze_gesture_from_input(user_input)
                
                # Step 2: Think (process with Gemini)
                self.display.set_expression("thinking")
                if special_gesture and gesture_name in ["Point"]:
                    # Use detected gesture for thinking if it's Point
                    special_gesture()
                else:
                    # Default thinking gesture
                    self.servos.point()
                
                print("[Thinking...]")
                response = self.llm.ask(user_input)
                print(f"Ash: {response}")
                
                # Step 3: Respond with appropriate gesture
                self.display.set_expression("speaking")
                
                # Use special gesture if detected (especially for greetings)
                if special_gesture and gesture_name:
                    print(f"[Gesture: {gesture_name}]")
                    special_gesture()
                
                self.audio.speak(response)
                
                # Step 4: Express happiness after responding
                self.display.set_expression("happy")
                
                # Final gesture based on context
                if special_gesture and gesture_name in ["Wave", "Arms Up"]:
                    # Keep the special gesture
                    pass
                else:
                    # Default happy gesture
                    self.servos.arms_up()
                
                # Step 5: Cooldown period
                print(f"[Cooldown: {self.cooldown}s]")
                time.sleep(self.cooldown)
                
            except KeyboardInterrupt:
                print("\n\nInterrupted by user")
                self.running = False
                break
            
            except Exception as e:
                print(f"\nError in interaction loop: {e}")
                self.display.set_expression("error")
                self.audio.speak("Sorry, I encountered an error.")
                time.sleep(2)
                # Continue running despite error
    
    def run(self):
        """
        Main run method - starts Ash robot.
        """
        try:
            # Startup
            self.startup_sequence()
            
            # Main loop
            self.interaction_loop()
            
        except KeyboardInterrupt:
            print("\n\nShutting down...")
        
        except Exception as e:
            print(f"\nFatal error: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # Always perform clean shutdown
            self.shutdown_sequence()


def signal_handler(sig, frame):
    """
    Handle Ctrl+C gracefully.
    """
    print("\n\nReceived shutdown signal")
    sys.exit(0)


def main():
    """
    Main entry point for Ash robot.
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Ash Desktop AI Robot - Your friendly AI assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 src/main.py           # Start with voice input (default)
  python3 src/main.py --text    # Start with text input only
  
Commands during interaction:
  • Type 'quit', 'exit', or 'bye' to exit
  • Type 'text' to switch to text input mode
  • Type 'voice' to switch to voice input mode
  • Press Ctrl+C to exit anytime
        """
    )
    parser.add_argument(
        '--text', '--text-only',
        action='store_true',
        help='Start in text-only input mode (no voice recognition)'
    )
    
    args = parser.parse_args()
    
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create and run robot
    ash = AshRobot(text_mode=args.text)
    ash.run()


if __name__ == "__main__":
    main()

