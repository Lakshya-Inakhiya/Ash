"""
Gestures Module for Ash Robot.

This module controls the servo motors via PCA9685 I2C servo driver board.
It provides high-level gesture functions for the robot's arm movements.
"""

import time
import math
from pathlib import Path

try:
    from board import SCL, SDA
    import busio
    from adafruit_pca9685 import PCA9685
    from adafruit_motor import servo
    HARDWARE_AVAILABLE = True
except ImportError:
    print("Warning: Adafruit libraries not available.")
    print("Servo control will run in simulation mode.")
    print("Install on Pi with: pip install adafruit-circuitpython-pca9685 adafruit-circuitpython-motor")
    HARDWARE_AVAILABLE = False


class ServoController:
    """
    Controls servo motors for robot gestures.
    
    This class interfaces with the PCA9685 servo driver board to control
    two MG995 servo motors for arm movements.
    """
    
    def __init__(self, config):
        """
        Initialize the servo controller.
        
        Args:
            config: Configuration dictionary with servo settings
        """
        self.config = config
        self.i2c_address = config['servos']['i2c_address']
        self.pwm_frequency = config['servos']['pwm_frequency']
        
        # Servo channels
        self.left_arm_channel = config['servos']['channels']['left_arm']
        self.right_arm_channel = config['servos']['channels']['right_arm']
        
        # Pulse width range (microseconds)
        self.pulse_min = config['servos']['pulse_range']['min']
        self.pulse_max = config['servos']['pulse_range']['max']
        self.pulse_center = config['servos']['pulse_range']['center']
        
        # Angle definitions
        self.angles = config['servos']['angles']
        
        # Transition speed
        self.transition_speed = config['servos']['transition_speed']
        
        # Current positions (degrees)
        self.left_position = 90
        self.right_position = 90
        
        # Hardware initialization
        self.pca = None
        self.left_servo = None
        self.right_servo = None
        
        if HARDWARE_AVAILABLE:
            self._init_hardware()
        else:
            print("Running in simulation mode (no actual servo control)")
    
    def _init_hardware(self):
        """
        Initialize the PCA9685 board and servo objects.
        """
        try:
            # Initialize I2C bus
            i2c = busio.I2C(SCL, SDA)
            
            # Initialize PCA9685
            self.pca = PCA9685(i2c, address=self.i2c_address)
            self.pca.frequency = self.pwm_frequency
            
            # Initialize servos with safe pulse width range for MG995
            self.left_servo = servo.Servo(
                self.pca.channels[self.left_arm_channel],
                min_pulse=self.pulse_min,
                max_pulse=self.pulse_max
            )
            
            self.right_servo = servo.Servo(
                self.pca.channels[self.right_arm_channel],
                min_pulse=self.pulse_min,
                max_pulse=self.pulse_max
            )
            
            print("Servo hardware initialized successfully")
            print(f"PCA9685 at address 0x{self.i2c_address:02X}")
            print(f"Left arm: Channel {self.left_arm_channel}")
            print(f"Right arm: Channel {self.right_arm_channel}")
            
        except Exception as e:
            print(f"Error initializing servo hardware: {e}")
            print("Falling back to simulation mode")
            self.pca = None
            self.left_servo = None
            self.right_servo = None
    
    def _move_servo_smooth(self, servo_obj, current_angle, target_angle, speed):
        """
        Move a servo smoothly from current to target angle.
        
        Args:
            servo_obj: Servo object to move
            current_angle: Current angle in degrees
            target_angle: Target angle in degrees
            speed: Transition time in seconds
        
        Returns:
            float: Final angle reached
        """
        if servo_obj is None:
            # Simulation mode
            print(f"  [SERVO] {current_angle}° → {target_angle}°")
            return target_angle
        
        # Calculate number of steps
        steps = max(int(abs(target_angle - current_angle)), 1)
        delay = speed / steps
        
        # Smooth transition
        for i in range(steps + 1):
            angle = current_angle + (target_angle - current_angle) * (i / steps)
            servo_obj.angle = angle
            time.sleep(delay)
        
        return target_angle
    
    def set_arm_angle(self, arm, angle, smooth=True):
        """
        Set a specific arm to a specific angle.
        
        Args:
            arm: "left" or "right"
            angle: Angle in degrees (0-180)
            smooth: Use smooth transition if True
        
        Returns:
            bool: True if successful
        """
        # Clamp angle to safe range
        angle = max(0, min(180, angle))
        
        if arm == "left":
            if smooth:
                self.left_position = self._move_servo_smooth(
                    self.left_servo, self.left_position, angle, self.transition_speed
                )
            else:
                if self.left_servo:
                    self.left_servo.angle = angle
                self.left_position = angle
            return True
            
        elif arm == "right":
            if smooth:
                self.right_position = self._move_servo_smooth(
                    self.right_servo, self.right_position, angle, self.transition_speed
                )
            else:
                if self.right_servo:
                    self.right_servo.angle = angle
                self.right_position = angle
            return True
        
        else:
            print(f"Warning: Unknown arm '{arm}'")
            return False
    
    def set_both_arms(self, left_angle, right_angle, smooth=True):
        """
        Set both arms to specific angles simultaneously.
        
        Args:
            left_angle: Left arm angle in degrees
            right_angle: Right arm angle in degrees
            smooth: Use smooth transition if True
        """
        self.set_arm_angle("left", left_angle, smooth)
        self.set_arm_angle("right", right_angle, smooth)
    
    # High-level gesture functions
    
    def neutral(self):
        """
        Move both arms to neutral position (90°).
        """
        print("[GESTURE] Neutral")
        neutral_angle = self.angles['neutral']
        self.set_both_arms(neutral_angle, neutral_angle, smooth=True)
    
    def arms_up(self):
        """
        Raise both arms up (~45°).
        """
        print("[GESTURE] Arms Up")
        angle = self.angles['arms_up']
        self.set_both_arms(angle, angle, smooth=True)
    
    def arms_down(self):
        """
        Lower both arms down (~135°).
        """
        print("[GESTURE] Arms Down")
        angle = self.angles['arms_down']
        self.set_both_arms(angle, angle, smooth=True)
    
    def wave(self, repetitions=3):
        """
        Wave with the left arm.
        
        Args:
            repetitions: Number of times to wave
        """
        print(f"[GESTURE] Wave (x{repetitions})")
        
        # Keep right arm neutral
        self.set_arm_angle("right", self.angles['neutral'], smooth=True)
        
        # Wave left arm
        wave_start = self.angles['wave_start']
        wave_end = self.angles['wave_end']
        
        for i in range(repetitions):
            self.set_arm_angle("left", wave_start, smooth=True)
            self.set_arm_angle("left", wave_end, smooth=True)
        
        # Return to neutral
        self.set_arm_angle("left", self.angles['neutral'], smooth=True)
    
    def point(self):
        """
        Point with the right arm (up at ~45°), left arm down.
        """
        print("[GESTURE] Point")
        self.set_arm_angle("left", self.angles['arms_down'], smooth=True)
        self.set_arm_angle("right", self.angles['point_up'], smooth=True)
    
    def reset(self):
        """
        Reset both arms to safe neutral position.
        This should be called on startup and shutdown.
        """
        print("[GESTURE] Reset to neutral")
        self.neutral()
    
    def test_servos(self):
        """
        Test function to verify servo operation.
        Sweeps through the full range of motion slowly.
        """
        print("Testing servo range of motion...")
        print("This will move both arms through their full range")
        
        # Start at neutral
        self.neutral()
        time.sleep(1)
        
        # Test left arm
        print("Testing left arm...")
        for angle in [45, 90, 135, 90]:
            self.set_arm_angle("left", angle, smooth=True)
            time.sleep(0.5)
        
        # Test right arm
        print("Testing right arm...")
        for angle in [45, 90, 135, 90]:
            self.set_arm_angle("right", angle, smooth=True)
            time.sleep(0.5)
        
        # Test both arms together
        print("Testing both arms together...")
        self.arms_up()
        time.sleep(1)
        self.arms_down()
        time.sleep(1)
        self.neutral()
        
        print("Servo test complete!")
    
    def close(self):
        """
        Clean up and disable servos.
        """
        # Move to neutral before disabling
        self.reset()
        
        # Disable PWM outputs
        if self.pca:
            self.pca.deinit()
        
        print("Servo controller closed")


def main():
    """
    Test function for the gestures module.
    """
    import sys
    sys.path.append(str(Path(__file__).parent))
    from utils import load_config
    
    print("Gestures Module Test")
    print("-" * 40)
    
    try:
        config = load_config()
        controller = ServoController(config)
        
        print("\nTesting all gestures...")
        print("(Watch the servo arms if hardware is connected)")
        
        # Test each gesture
        gestures = [
            ("Neutral", controller.neutral),
            ("Arms Up", controller.arms_up),
            ("Arms Down", controller.arms_down),
            ("Point", controller.point),
            ("Wave", controller.wave),
            ("Neutral", controller.neutral),
        ]
        
        for name, gesture_func in gestures:
            print(f"\n-> {name}")
            gesture_func()
            time.sleep(2)
        
        # Full test if user wants
        print("\n" + "=" * 40)
        response = input("Run full servo range test? (y/n): ")
        if response.lower() == 'y':
            controller.test_servos()
        
        controller.close()
        print("\nTest complete!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

