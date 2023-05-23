import asyncio
import copy
import json
import logging
import multiprocessing
import os
from json import JSONDecodeError

from watchdog.observers import Observer

from dadou_utils.com.input_messages_list import InputMessagesList
# from dadou_utils.com.lora_radio import LoraRadio
# from dadou_utils.com.serial_device import SerialDevice
from dadou_utils.com.ws_server import WsServer
from dadou_utils.static_value import StaticValue
from dadou_utils.utils.time_utils import TimeUtils
from dadou_utils.utils_static import INPUT_MESSAGE_FILE, RANDOM, MAIN_THREAD, NEW_DATA, TYPES, MULTI_THREAD, \
    INPUT_MESSAGE_DIRECTORY, PROCESS_NAME, LOCK, INPUT_LOCK, SINGLE_THREAD, WHEELS
from dadourobot.input.file_watcher import FileWatcher
from dadourobot.robot_config import config


class GlobalReceiver:

    prefix = '<'
    postfix = '>'
    messages = InputMessagesList()
    last_msg_file_modif = 0
    last_msg = {}
    new_data = False

    def __init__(self, config, animation_manager=None):
        #self.mega_lora_radio = SerialDevice('modem', self.config.RADIO_MEGA_ID, 7)
        #self.mega_lora_radio = device_manager.get_device(RobotStatic.RADIO_MEGA)
        #glove_id = SerialDevice.USB_ID_PATH + "usb-Raspberry_Pi_Pico_E6611CB6976B8D28-if00"
        #self.glove = SerialDevice(glove_id)
        self.config = config
        if TYPES in config:
            self.types = config[TYPES]
        self.main_thread = MAIN_THREAD in config and config[MAIN_THREAD]

        if self.main_thread:
            WsServer().start()
        #self.lora_radio = LoraRadio(self.config)
        self.last_msg_time = 0
        self.animation_manager = animation_manager

        if not config[SINGLE_THREAD]:
            self.check_file_change()

        #if config[MULTI_THREAD]:
        #    self.file_watcher = FileWatcher()
        #    observer = Observer()
        #    observer.schedule(self.file_watcher, path=INPUT_MESSAGE_DIRECTORY, recursive=True)
        #    observer.start()

    def get_msg(self):
        #TODO mettre a jour la logique lora pour qu'elle corresponde a la logique dict ws
        #mega_msg = self.mega_lora_radio.get_msg()
        #if mega_msg:
        #    logging.info('received radio msg : {}'.format(mega_msg))
        #    return self.filter_msg(mega_msg)
        """glove = self.glove.get_msg()
        if glove:
            logging.info('received glove msg : {}'.format(glove))
            return glove"""

        msg = self.messages.pop_msg()
        if msg:
            if self.animation_manager:
                self.animation_manager.update(msg)

        if self.animation_manager and not self.animation_manager.playing and self.config[RANDOM]:
            self.animation_manager.random()
            #return self.write_msg(self.animation_manager.event())

        if self.animation_manager:
            msg.update(self.animation_manager.event())

        if msg and len(msg) > 0:
            logging.info('return msg {}'.format(msg))
            return msg

        #radio_msg = self.lora_radio.receive_msg()
        #if radio_msg:
        #    logging.info('received lora msg : {}'.format(radio_msg))
        #    return radio_msg

    def check_file_change(self):
        if not config[SINGLE_THREAD]:
            if os.path.isfile(INPUT_MESSAGE_FILE):
                new_modif = os.path.getmtime(INPUT_MESSAGE_FILE)
                if new_modif != self.last_msg_file_modif:
                    logging.debug('file modified')
                    self.new_data = True
                    self.last_msg_file_modif = new_modif

    def multi_get(self):
        if self.main_thread:
            msg = self.get_msg()
            if msg:
                if not config[SINGLE_THREAD]:
                    self.write_msg_plus_time(msg)
                return msg
        else:
            self.check_file_change()
            return self.get_file_msg()

    def write_msg(self, msg):
        if not config[SINGLE_THREAD]:
            asyncio.run(self.write_msg_async(msg))

    async def write_msg_async(self, msg):
        self.create_lock()
        if msg:
            json_object = json.dumps(msg, indent=4)
            with open(INPUT_MESSAGE_FILE, "w") as j:
                j.write(json_object)
            logging.info("new msg written {}".format(msg))
        else:
            with open(INPUT_MESSAGE_FILE, "w") as j:
                j.write("")
            logging.debug("delete msg on disk")
        self.delete_lock()

    def write_msg_plus_time(self, msg):
        t = TimeUtils.current_milli_time()
        time_msg = copy.copy(msg)
        for key in msg.keys():
            if not isinstance(msg[key], list):
            #if len(msg[key]):
                time_msg[key] = [t, msg[key]]
            else:
                time_msg[key] = msg[key]

        self.write_msg(time_msg)

    def write_values(self, values):
        msg = copy.copy(self.last_msg)
        msg.update(values)
        self.write_msg(msg)

    def get_file_msg(self):
        if self.new_data:
            self.new_data = False
            with multiprocessing.Lock():
                msg = self.decode_file_msg()
            return msg

    @staticmethod
    def msg_locked():
        return os.path.isfile(INPUT_LOCK)

    @staticmethod
    def create_lock():
        logging.info("create lock")
        with open(INPUT_LOCK, "w") as lock:
            lock.write("")

    @staticmethod
    def delete_lock():
        if os.path.isfile(INPUT_LOCK):
            try:
                os.remove(INPUT_LOCK)
            except FileNotFoundError:
                logging.error("no lock found")
        else:
            logging.error("no lock found")

    def read_msg(self):
        while self.msg_locked():
            pass
        with open(INPUT_MESSAGE_FILE, 'r') as j:
            try:
                return json.loads(j.read())
            except JSONDecodeError:
                logging.debug("{} wrong format {}".format(INPUT_MESSAGE_FILE, j))

    def decode_file_msg(self):

        msg_from_file = self.read_msg()
        new_msg = {}
        if msg_from_file:
            for key in msg_from_file.keys():
                if isinstance(msg_from_file[key], list):
                    if key in self.last_msg:
                        if not isinstance(self.last_msg[key], list):
                            # TODO fix this
                            if key != WHEELS:
                                new_msg[key] = msg_from_file[key][1]
                        else:
                            if not self.last_msg[key][0] == msg_from_file[key][0]:
                                # TODO fix this
                                if key != WHEELS:
                                    new_msg[key] = msg_from_file[key][1]
                    else:
                        #TODO fix this
                        if key != WHEELS:
                            new_msg[key] = msg_from_file[key][1]
                        else:
                            new_msg[key] = msg_from_file[key]
                else:
                    new_msg[key] = msg_from_file[key]
            self.last_msg = msg_from_file
        else:
            logging.debug("msg from file empty")
        return new_msg

    def return_msg(self, msg, log_text):
        if msg:
            logging.info(log_text.format(msg))
            return msg
    #def filter_msg(self, m):
    #    return self.msg.set(m)


