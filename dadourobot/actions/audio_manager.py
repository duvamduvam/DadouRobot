# pip3 install sound-player
# https://github.com/Krozark/sound-player/blob/master/example.py
import logging
import threading
from os.path import exists
from sound_player import Sound, SoundPlayer

from dadourobot.robot_static import RobotStatic
from dadourobot.path_time import PathTime
from dadourobot.robot_factory import RobotFactory

from dadou_utils.audios.sound_object import SoundObject


class AudioManager:

    player = SoundPlayer()
    silence = "audios/silence.wav"
    playlist = []
    current_audio = None
    current_audio_name = None

    def __init__(self):
        self.json_manager = RobotFactory().robot_json_manager

    def play_sounds_bak(self, audios):
        self.player.stop()
        for audio in audios:
            logging.info("enqueue: " + audio.get_path())
            self.player.enqueue(Sound(audio.get_path()), 1)
            for s in range(int(audio.get_time())):
                self.player.enqueue(Sound(self.silence), 1)
        self.player.play()

    def play_sound(self, audio):
        if exists(RobotStatic.AUDIOS_DIRECTORY+audio['path']):
            self.current_audio = SoundObject(RobotStatic.AUDIOS_DIRECTORY, audio['path'])
            self.current_audio.play()
            self.current_audio_name = audio['path']
        else:
            logging.error("audio {} don't exist".format(audio['path']))

    def is_playing(self):
        if not self.current_audio or not self.current_audio.is_playing():
            return False
        return True

    def play_sounds(self, audios):
        self.player.stop()
        for audio in audios:
            logging.info("enqueue: " + audio.get_path())

            sound = SoundObject(RobotStatic.AUDIOS_DIRECTORY, audio.get_path())
            self.playlist.append(sound)
            #self.player.enqueue(Sound(audio.get_path()), 1)
            #for s in range(int(audio.get_time())):
            #    self.player.enqueue(Sound(self.silence), 1)
            sound.play()
        #self.player.play()

    def stop_sound(self):
        if self.current_audio:
            self.current_audio.stop()
            self.current_audio_name = ""

    def process(self, msg):
        if msg and hasattr(msg, 'key'):
            logging.debug("number of thread : {}".format(threading.active_count()))
            audio_path = self.json_manager.get_audios(msg.key)
            if audio_path:
                if audio_path['path'] == self.current_audio_name:
                    logging.debug("already playing {}".format(self.current_audio_name))
                    return
                if audio_path['name'] == 'stop':
                    self.stop_sound()
                    logging.info("stop sound")
                else:
                    if self.current_audio:
                        self.current_audio.stop()
                    self.current_audio_name = audio_path['path']
                    self.play_sound(audio_path)


            """           audio_sequence = self.json_manager.get_audio_seq(key)
            if audio_sequence:
                logging.info("play new audio")
                audios = []
                for audio_seq in audio_sequence[RobotStatic.SEQUENCE]:
                    audio_path = self.json_manager.get_audio_path_by_name(audio_seq[RobotStatic.NAME])
                    logging.debug("audios name : " + audio_seq[RobotStatic.NAME] + " path : " + audio_path)
                    audios.append(PathTime(audio_path, audio_seq[RobotStatic.DELAY]))

                self.play_sounds(audios)"""

