# -*- coding: utf-8 -*-

from imio.helpers import barcode

import os
import unittest


class TestBarcode(unittest.TestCase):

    def test_generate_barcode(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        barcode_resource = "barcode_python2_zint_60x60_278bytes.png"
        with open(os.path.join(current_dir, barcode_resource), 'rb') as barcode_file:
            bc = barcode_file.read()
            result = barcode.generate_barcode('123')
            result = result.read()
            self.assertEqual(bc, result)

    def test_generate_barcode_filetype(self):
        result = barcode.generate_barcode('123', filetype='GIF')
        self.assertTrue(result.read().startswith(b'GIF'))

    def test_generate_barcode_missing_executable(self):
        self.assertRaises(OSError, barcode.generate_barcode, '123',
                          executable='zints')
