import logging

import adafruit_pcf8574
import board

from dadou_utils.utils.time_utils import TimeUtils
from dadou_utils.utils_static import KEY, I2C_ENABLED, DIGITAL_CHANNELS_ENABLED, JSON_RELAYS, RELAY, NAME
from dadourobot.actions.abstract_json_actions import AbstractJsonActions


class RelaysManager(AbstractJsonActions):

    OCTAVER = "octaver"
    HF_RECEIVER = "hf_receiver"
    EFFECT = "effect_on"
    VOICE_OUT = "voice_out"

    NORMAL_VOICE = "normal_voice"
    PITCHED_VOICE = "pitched_voice"

    def __init__(self, config, receiver, json_manager):
        super().__init__(config=config, json_manager=json_manager, json_file=config[JSON_RELAYS], action_type=RELAY)
        self.receiver = receiver
        self.config = config
        if not self.config[I2C_ENABLED] or not self.config[DIGITAL_CHANNELS_ENABLED]:
            logging.warning("i2c digital disabled")
            return

        self.json_manager = json_manager

        i2c = board.I2C()  # uses board.SCL and board.SDA
        pcf = adafruit_pcf8574.PCF8574(i2c, address=0x21)

        self.power_hf = pcf.get_pin(3)
        self.power_hf.value = True
        self.power_effect = pcf.get_pin(2)
        self.power_effect.value = True
        self.effect = pcf.get_pin(1)
        self.effect.value = True
        self.voice_out = pcf.get_pin(0)
        self.voice_out.value = True

        self.last_effect_time = 0
        self.effect_timeout = 800

    def update(self, msg):

        if not self.config[I2C_ENABLED] or not self.config[DIGITAL_CHANNELS_ENABLED]:
            return msg

        json_seq = self.get_sequence(msg, True)

        if json_seq:
            relay = self.sequences_key[msg[KEY]]

            if relay[NAME] == self.PITCHED_VOICE:
                self.voice_out.value = False
                self.effect.value = True
                self.last_effect_time = TimeUtils.current_milli_time()
                logging.info("switch effect on")

            if relay[NAME] == self.NORMAL_VOICE:
                self.voice_out.value = False
                self.effect.value = False
                self.last_effect_time = TimeUtils.current_milli_time()
                logging.info("switch effect on")

            if relay[NAME] == self.OCTAVER:
                self.power_effect.value = not self.power_effect.value
                logging.info("switch octaver {}".format(self.power_effect.value))

            if relay[NAME] == self.HF_RECEIVER:
                self.power_hf.value = not self.power_hf.value
                logging.info("switch hf receiver {}".format(self.power_hf.value))

            if relay[NAME] == self.EFFECT:
                #self.effect.value = True
                self.voice_out.value = False
                self.last_effect_time = TimeUtils.current_milli_time()
                logging.info("switch effect on")
        return msg

    def process(self):

        if not self.config[I2C_ENABLED] or not self.config[DIGITAL_CHANNELS_ENABLED]:
            return

        if not self.voice_out.value and TimeUtils.is_time(self.last_effect_time, self.effect_timeout):
            #self.effect.value = False
            self.voice_out.value = True

            logging.info("activate effect off")
