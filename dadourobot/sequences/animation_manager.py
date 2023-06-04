import logging
import os
import random

from dadou_utils.files.files_utils import FilesUtils
from dadou_utils.utils.time_utils import TimeUtils
from dadou_utils.utils_static import ANIMATION, STOP_ANIMATION_KEYS, AUDIO, AUDIOS, KEY, NECK, NECKS, FACE, FACES, \
    LIGHTS, WHEELS, NAME, \
    DURATION, KEYS, RANDOM, START, STOP, TYPES, SEQUENCES_DIRECTORY, LOOP_DURATION, RANDOM_ANIMATION_LOW, \
    RANDOM_ANIMATION_HIGH, BASE_PATH, \
    LEFT_ARM, RIGHT_ARM, STOP_KEY, LEFT_EYE, RIGHT_EYE

from dadourobot.actions.abstract_actions import ActionsAbstract
from dadourobot.sequences.animation import Animation
from dadourobot.sequences.random_animation_start import RandomAnimationStart


class AnimationManager(ActionsAbstract):

    current_key = None
    playing = False
    start = False

    last_time = 0
    timeout = 0
    random_duration = 0
    last_random = 0

    datas = None
    duration = 0

    audios_animation = None
    left_arm_animation = None
    right_arm_animation = None
    left_eye_animation = None
    right_eye_animation = None
    necks_animation = None
    faces_animation = None
    lights_animation = None
    wheels_animation = None

    current_animation = None

    def __init__(self, config, json_manager):
        self.config = config
        super().__init__(json_manager, None)
        self.load_animation_sequences()
        self.stop_keys = self.config[STOP_ANIMATION_KEYS]
        self.random_animation_sequence = []
        self.random_duration = random.randint(self.config[RANDOM_ANIMATION_LOW], self.config[RANDOM_ANIMATION_HIGH])
        RandomAnimationStart.value = TimeUtils.current_milli_time()
        logging.debug("random duration time {}".format(self.random_duration))
        self.load_random_animation_sequences()

    def load_animation_sequences(self):
        sequences_files = FilesUtils.get_folder_files(self.config[BASE_PATH]+self.config[SEQUENCES_DIRECTORY])
        for sequence_file in sequences_files:
            json_sequence = FilesUtils.open_json(sequence_file, 'r')
            json_sequence[NAME] = os.path.basename(sequence_file).replace(".json", "")
            self.sequences_key[json_sequence[KEYS]] = json_sequence
            self.sequences_name[json_sequence[NAME]] = json_sequence

    def load_random_animation_sequences(self):
        for seq_key in self.sequences_name.keys():
            sequence = self.sequences_name[seq_key]
            if TYPES in sequence.keys():
                for t in sequence[TYPES]:
                    if t == RANDOM:
                        self.random_animation_sequence.append(sequence[NAME])

    def random(self):
        if TimeUtils.is_time(RandomAnimationStart.value, self.random_duration):
            if len(self.random_animation_sequence) > 0:
                random_index = random.randint(0, len(self.random_animation_sequence)-1)
                RandomAnimationStart.value = TimeUtils.current_milli_time()
                self.update({ANIMATION: self.random_animation_sequence[random_index]})
                self.random_duration = random.randint(self.config[RANDOM_ANIMATION_LOW],
                                                      self.config[RANDOM_ANIMATION_HIGH])
                logging.info('random animation {}'.format(self.random_animation_sequence[random_index]))

    def update(self, msg):
        if msg and KEY in msg and msg[KEY] in self.config[STOP_KEY]:
            return msg.update(self.stop())
        self.get_animation(msg)
        return msg

    def get_animation(self, msg):
        animation = self.get_sequence(msg, ANIMATION, False)

        if not animation:
            #self.duration = 0
            return

        self.current_animation = animation
        logging.info('start animation {}'.format(self.current_animation[NAME]))

        self.playing = True
        self.start = True

        if DURATION in msg:
            self.duration = msg[DURATION]
        else:
            self.duration = self.current_animation[DURATION]
            
        self.last_time = TimeUtils.current_milli_time()
        self.last_random = TimeUtils.current_milli_time()

        self.audios_animation = Animation(self.current_animation, self.duration, AUDIOS)
        self.left_arm_animation = Animation(self.current_animation, self.duration, LEFT_ARM)
        self.right_arm_animation = Animation(self.current_animation, self.duration, RIGHT_ARM)
        self.left_eye_animation = Animation(self.current_animation, self.duration, LEFT_EYE)
        self.right_eye_animation = Animation(self.current_animation, self.duration, RIGHT_EYE)
        self.necks_animation = Animation(self.current_animation, self.duration, NECK)
        self.faces_animation = Animation(self.current_animation, self.duration, FACES)
        self.lights_animation = Animation(self.current_animation, self.duration, LIGHTS)
        self.wheels_animation = Animation(self.current_animation, self.duration, WHEELS)

    def stop(self):
        if self.playing:
            logging.info('stop animation')
            self.playing = False
        return {ANIMATION: False}
    def event(self):
        if self.playing and TimeUtils.is_time(self.last_time, self.duration):
            return self.stop()

        if not self.playing:
            return {}

        events = {}

        if self.start:
            events[ANIMATION] = True
            events[DURATION] = self.duration
            self.start = False

        self.fill_event(events, AUDIO, self.audios_animation)
        self.fill_event(events, LEFT_ARM, self.left_arm_animation)
        self.fill_event(events, RIGHT_ARM, self.right_arm_animation)
        self.fill_event(events, LEFT_EYE, self.left_eye_animation)
        self.fill_event(events, RIGHT_EYE, self.right_eye_animation)
        self.fill_event(events, NECK, self.necks_animation)
        self.fill_event(events, WHEELS, self.wheels_animation)
        self.fill_event(events, FACE, self.faces_animation)
        self.fill_event(events, LIGHTS, self.lights_animation)
        if len(events) > 0:
           logging.warning('update animation {} with values {}'.format(self.current_animation[NAME], events))
        return events

    def fill_event(self, events, key, animation):
        if not animation or not animation.has_data:
            return
        event_action = animation.next()
        if event_action:
            events[key] = event_action

    def process(self):
        pass