# -*- coding: utf-8 -*-

from imio.helpers import barcode

import os
import unittest


class TestBarcode(unittest.TestCase):
    def test_generate_barcode(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        barcode_resource = "barcode_python3_zint_60x60_156bytes.png"
        with open(os.path.join(current_dir, barcode_resource), "rb") as barcode_file:
            bc = barcode_file.read()
            result = barcode.generate_barcode("123")
            result = result.read()
            self.assertEqual(bc, result)

    def test_generate_barcode_filetype(self):
        result = barcode.generate_barcode("123", filetype="GIF")
        self.assertTrue(result.read().startswith(b"GIF"))

    def test_generate_barcode_missing_executable(self):
        self.assertRaises(OSError, barcode.generate_barcode, "123", executable="zints")

    def test_generate_barcode_resize(self):
        from PIL import Image

        original = Image.open(barcode.generate_barcode("123"))
        resized = Image.open(barcode.generate_barcode("123", resize=0.5))
        self.assertEqual(resized.size, (int(round(original.width * 0.5)),
                                       int(round(original.height * 0.5))))

    def test_generate_barcode_resize_none(self):
        ref = barcode.generate_barcode("123").read()
        same = barcode.generate_barcode("123", resize=None).read()
        self.assertEqual(ref, same)

    def test_generate_barcode_resize_ignored_for_non_raster(self):
        # SVG is not a PIL raster format; resize must be silently ignored.
        result = barcode.generate_barcode("123", filetype="SVG", resize=0.5).read()
        self.assertTrue(result.lstrip().startswith(b"<"))
