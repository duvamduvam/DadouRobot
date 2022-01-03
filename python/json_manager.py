import json
import logging

import jsonpath_rw_ext


class JsonManager:
    with open("json/colors.json", 'r') as json_file:
        colors = json.load(json_file)

    with open("json/face_sequence.json", 'r') as json_file:
        face_seq = json.load(json_file)

    with open("json/lights.json", 'r') as json_file:
        lights = json.load(json_file)

    with open("json/visual.json", 'r') as json_file:
        visual = json.load(json_file)

    def get_visual_path(self, key) -> str:
        result = jsonpath_rw_ext.match('$.visual[?name==' + key + ']', self.visual)
        if len(result) == 0:
            logging.error("no visual path for " + key)
            return
        logging.debug(result)
        return result[0]['path']

    def get_face_part(self, name) -> str:
        result = jsonpath_rw_ext.match('$.part_seq[?name==' + name + ']', self.face_seq)
        if len(result) == 0:
            logging.error("no visual path for " + name)
            return
        logging.debug(result)
        return result[0]

    def get_all_visual(self):
        result = jsonpath_rw_ext.match('$.visual[*]', self.visual)
        logging.debug(result)
        return result

    def get_face_seq(self, key):
        result = jsonpath_rw_ext.match('$.main_seq[?keys~' + key + ']', self.face_seq)
        logging.debug(result)
        return result[0]

    def get_part_seq(self, name):
        result = jsonpath_rw_ext.match('$.part_seq[?name==' + name + ']', self.face_seq)
        logging.debug(result)
        return result[0]

    def get_lights(self, key):
        result = jsonpath_rw_ext.match('$.lights[?keys~' + key + ']', self.lights)
        logging.debug(result)
        return result[0]

    def get_color(self, key):
        result = jsonpath_rw_ext.match('$.colors[?name~' + key + ']', self.colors)
        logging.debug(result)
        color = (int(result[0]['red']), int(result[0]['green']), int(result[0]['blue']))
        return color
