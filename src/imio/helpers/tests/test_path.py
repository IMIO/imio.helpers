# -*- coding: utf-8 -*-

import unittest
from imio.helpers import path
from imio.helpers import browser


class TestPath(unittest.TestCase):

    def test_path_to_package(self):
        self.assertTrue(path.path_to_package(path).
                        endswith('/src/imio/helpers/'))
        self.assertTrue(path.path_to_package(browser,
                                             filepart='static/listing.js').
                        endswith('/src/imio/helpers/browser/static/listing.js'))
