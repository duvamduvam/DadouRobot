from dadou_utils.utils_static import I2C_ENABLED, PWM_CHANNELS_ENABLED, LEFT_ARM, LEFT_ARM_NB, RIGHT_ARM, RIGHT_ARM_NB
from dadou_utils.actions.servo_abstract import ServoAbstract


MIN_PWM = 5000
MAX_PWM = 65530

DEFAULT_POS = 180


class RightArm(ServoAbstract):

    SERVO_MIN = 0
    SERVO_MAX = 180
    DEFAULT_POS = 0

    def __init__(self, config):

        super().__init__(RIGHT_ARM, config[RIGHT_ARM_NB], self.DEFAULT_POS, self.SERVO_MAX, config[I2C_ENABLED], config[PWM_CHANNELS_ENABLED])
