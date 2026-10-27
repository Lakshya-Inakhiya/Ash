"""Arm servos via a PCA9685 board. Falls back to logging without hardware."""

import time

try:
    import board
    from adafruit_motor import servo
    from adafruit_pca9685 import PCA9685
except (ImportError, NotImplementedError, RuntimeError):
    board = None

from ash.brain import GESTURES, gesture_poses


class ServoController:
    def __init__(self, cfg, angles):
        """cfg: the `servos` section of hardware/settings.yaml. angles: brain gesture angles."""
        self.angles = angles
        self.speed = cfg["transition_speed"]
        self.position = {"left": angles["neutral"], "right": angles["neutral"]}
        self.servos = {}
        self.pca = None

        if board is None:
            print("Servo libraries not available; gestures will only be logged.")
            return
        try:
            self.pca = PCA9685(board.I2C(), address=cfg["i2c_address"])
            self.pca.frequency = cfg["pwm_frequency"]
            pulse = cfg["pulse_range"]
            for arm, channel in cfg["channels"].items():
                self.servos[arm.removesuffix("_arm")] = servo.Servo(
                    self.pca.channels[channel], min_pulse=pulse["min"], max_pulse=pulse["max"]
                )
            print(f"Servos ready (PCA9685 at 0x{cfg['i2c_address']:02X})")
        except Exception as e:
            print(f"Servo board not found ({e}); gestures will only be logged.")
            self.pca = None

    def move(self, arm, target):
        """Sweep one arm to target degrees over transition_speed seconds."""
        target = max(0, min(180, target))
        start = self.position[arm]
        motor = self.servos.get(arm)
        if motor:
            steps = max(int(abs(target - start)), 1)
            for i in range(1, steps + 1):
                motor.angle = start + (target - start) * i / steps
                time.sleep(self.speed / steps)
        self.position[arm] = target

    def neutral(self):
        self.move("left", self.angles["neutral"])
        self.move("right", self.angles["neutral"])

    def perform(self, gesture):
        """Play a gesture from the brain, then return to neutral."""
        for left, right in gesture_poses(gesture, self.angles):
            self.move("left", self.angles["neutral"] if left is None else left)
            self.move("right", self.angles["neutral"] if right is None else right)
        self.neutral()

    def close(self):
        self.neutral()
        if self.pca:
            self.pca.deinit()


if __name__ == "__main__":
    from ash.config import load_config

    arms = ServoController(load_config("hardware/settings.yaml")["servos"], load_config()["gestures"])
    for name in GESTURES:
        print(name)
        arms.perform(name)
        time.sleep(1)
    arms.close()
