# -*- coding: utf-8 -*-

from imio.helpers import barcode

import os
import unittest


class TestBarcode(unittest.TestCase):

    def test_generate_barcode(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        barcode_file = open(os.path.join(current_dir, 'barcode.png'), 'r')
        result = barcode.generate_barcode('123')
        self.assertEqual(barcode_file.read(), result.read())

    def test_generate_barcode_missing_executable(self):
        self.assertRaises(OSError, barcode.generate_barcode, '123',
                          executable='zints')
