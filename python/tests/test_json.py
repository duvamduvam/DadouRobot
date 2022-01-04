import logging.config
from python.tests.conf_test import TestSetup
from python.visual import Visual

TestSetup()

import json

import os
import pathlib
import sys
import time
import unittest
import jsonpath_rw_ext
from jsonpath_ng.ext import parse
import jsonpath_ng


from python.json_manager import JsonManager

class TestJson(unittest.TestCase):

    json_manager = JsonManager()

    def test_get_main_seq(self, params):
        result = self.json_manager.get_face_seq("A1")
        logging.info(result)

    @unittest.skip
    def test_json_path(self, params):
        with open("json/face_sequence.json", 'r') as json_file:
            json_data = json.load(json_file)
        list_val = jsonpath_rw_ext.match('$.face_seq[?name==speak]', json_data)
        print(list_val[0]['sequence'])
        #logging.error("test45")

    @unittest.skip
    def test_get_visual_path(self, params):
        result = self.json_manager.get_visual_path("mopen1")
        print(result)

    @unittest.skip
    def test_get_face_seq(self, params):
        result = self.json_manager.get_face_seq("speak")
        print(result)

    @unittest.skip
    def test_get_all_visual(self, params):
        print("load all visual")
        visuals_path = self.json_manager.get_all_visual()
        for visual_path in visuals_path:
            self.visuals.append(Visual(visual_path['name'], visual_path['path']))

        result = self.json_manager.get_all_visual()
        print(result)
