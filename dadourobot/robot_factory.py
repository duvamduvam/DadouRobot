import logging
import logging.config
import os

import neopixel
from dadou_utils.com.serial_devices_manager import SerialDeviceManager
from microcontroller import Pin

from dadourobot.actions.audios import AudioManager
from dadourobot.actions.expressions import Face
from dadourobot.bak.head import Head
#from dadourobot.actions.lights import Lights
from dadourobot.actions.lights import Lights
from dadourobot.actions.neck import Neck
from dadourobot.actions.wheel import Wheel
from dadourobot.config import RobotConfig
from dadourobot.files.robot_json_manager import RobotJsonManager

from dadou_utils.singleton import SingletonMeta

from dadourobot.robot_static import LOGGING_CONFIG_FILE, JSON_CONFIG, JSON_DIRECTORY, DEVICES
from dadourobot.sequences.animation_manager import AnimationManager


class RobotFactory(metaclass=SingletonMeta):

    def __init__(self):
        base_path = os.getcwd()
        logging_file = base_path+LOGGING_CONFIG_FILE
        print(logging_file)
        logging.config.fileConfig(logging_file, disable_existing_loggers=False)

        self.robot_json_manager = RobotJsonManager(base_path, JSON_DIRECTORY, JSON_CONFIG)
        self.device_manager = SerialDeviceManager(self.robot_json_manager.get_config_item(DEVICES))
        self.config = RobotConfig(self.robot_json_manager)

        self.audio = AudioManager(self.robot_json_manager)
        self.head = Head(self.device_manager, self.config)
        self.wheel = Wheel(self.config)


        #TODO improve led lights
        self.pixels = neopixel.NeoPixel(Pin(self.config.FACE_PIN), 782, auto_write=False, brightness=0.05, pixel_order=neopixel.GRB)

        """pixel_pin = board.D18
        num_pixels = 30
        ORDER = neopixel.GRB

        self.pixels = neopixel.NeoPixel(
            pixel_pin, num_pixels, brightness=0.2, auto_write=False, pixel_order=ORDER
        )"""

        self.face = Face(self.robot_json_manager, self.config, self.pixels)
        self.lights = Lights(self.config, self.robot_json_manager, self.pixels)
        self.neck = Neck(self.config)

        self.animation_manager = AnimationManager(self.robot_json_manager, self.config)

    def get_strip(self):
        return self.pixels

    def get_audio(self):
        return self.audio
