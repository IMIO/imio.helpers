# -*- coding: utf-8 -*-

from imio.helpers import browser
from imio.helpers import path

import os
import unittest


class TestPath(unittest.TestCase):
    def test_path_to_package(self):
        self.assertTrue(path.path_to_package(path).endswith("/src/imio/helpers/"))
        self.assertTrue(
            path.path_to_package(browser, filepart="static/listings.js").endswith(
                "/src/imio/helpers/browser/static/listings.js"
            )
        )

    def test_is_test_url(self):
        os.environ["PUBLIC_URL"] = ""
        self.assertFalse(path.is_test_url())
        os.environ["PUBLIC_URL"] = "http://example.com"
        self.assertFalse(path.is_test_url())
        os.environ["PUBLIC_URL"] = "https://xxx.imio-test.be"
        self.assertTrue(path.is_test_url())
        os.environ["PUBLIC_URL"] = "https://xxx.imio-acceptation.be"
        self.assertTrue(path.is_test_url())
