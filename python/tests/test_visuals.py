import logging.config
from python.tests.test_setup import TestSetup
TestSetup()

import unittest
import logging

from python.tests.test_setup import TestSetup
from python.visual import Image


class MyTestCase(unittest.TestCase):
    TestSetup()

    def test_load(self):
        image = Image("../../visuals/")
        image.load_images()
        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
