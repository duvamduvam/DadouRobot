import logging
import pwmio
import board
from digitalio import DigitalInOut, Direction, Pull
from utils import Utils


class Wheel:
    left, right = 0

    # TODO check steps
    pwm_step = 50
    time_step = 50
    last_time = Utils.current_milli_time()

    # TODO update board pin
    left_pwm = pwmio.PWMOut(board.LED, frequency=5000, duty_cycle=0)
    right_pwm = pwmio.PWMOut(board.LED, frequency=5000, duty_cycle=0)
    dir_lef = DigitalInOut(board.LED)
    dir_right = DigitalInOut(board.LED)
    utils = Utils()

    def update(self, key: str):
        self.update_dir(key[0], self.dir_left)
        self.update_dir(key[0], self.dir_right)
        left = self.utils.translate(key[0])
        right = self.utils.translate(key[1])
        logging.debug("update wheel with key : " + key)

    def stop(self):
        self.left_pwm.duty_cycle = 0
        self.right_pwm.duty_cycle = 0

    def process(self):
        logging.debug("process wheel")
        if (self.left_pwm.duty_cycle != self.left and self.right_pwm.duty_cycle != self.right) \
                and Utils.current_milli_time() - self.last_time > self.time_step:
            self.update_pwm(self.left, self.left_pwm.duty_cycle)
            self.update_pwm(self.right, self.right_pwm.duty_cycle)
        else:
            self.last_time = Utils.current_milli_time()

    def update_pwm(self, target, pwm: pwmio.PWMOut):
        if pwm.duty_cycle < target:
            if (target - pwm.duty_cycle) < self.pwm_step:
                pwm.duty_cycle = target
            else:
                pwm.duty_cycle += self.setp
        else:
            if (pwm.duty_cycle - target) < self.pwm_step:
                pwm.duty_cycle = target
            else:
                pwm.duty_cycle -= self.setp

    def update_dir(self, key, digital):
        if self.utils.is_positive(key):
            digital = True
        else:
            digital = False