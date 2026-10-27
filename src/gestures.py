"""Arm gestures via a PCA9685 servo board. Falls back to logging without hardware."""

import time

try:
    import board
    from adafruit_motor import servo
    from adafruit_pca9685 import PCA9685
except (ImportError, NotImplementedError, RuntimeError):
    board = None


class ServoController:
    def __init__(self, config):
        cfg = config["servos"]
        self.angles = cfg["angles"]
        self.speed = cfg["transition_speed"]
        self.position = {"left": 90, "right": 90}
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

    def both(self, left, right):
        self.move("left", left)
        self.move("right", right)

    def neutral(self):
        self.both(self.angles["neutral"], self.angles["neutral"])

    def arms_up(self):
        self.both(self.angles["arms_up"], self.angles["arms_up"])

    def arms_down(self):
        self.both(self.angles["arms_down"], self.angles["arms_down"])

    def point(self):
        self.both(self.angles["arms_down"], self.angles["point_up"])

    def wave(self, repetitions=3):
        self.move("right", self.angles["neutral"])
        for _ in range(repetitions):
            self.move("left", self.angles["wave_start"])
            self.move("left", self.angles["wave_end"])
        self.move("left", self.angles["neutral"])

    def close(self):
        self.neutral()
        if self.pca:
            self.pca.deinit()


if __name__ == "__main__":
    from utils import load_config

    arms = ServoController(load_config())
    for name in ["neutral", "arms_up", "arms_down", "point", "wave", "neutral"]:
        print(name)
        getattr(arms, name)()
        time.sleep(1)
    arms.close()
