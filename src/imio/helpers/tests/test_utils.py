from imio.helpers.utils import is_valid_json
from Products.CMFPlone.utils import safe_unicode
from zope.interface import Invalid

import unittest


class TestUtils(unittest.TestCase):
    def test_valid_json(self):
        malicious_input = safe_unicode(""" ""};<script>alert('I'm malicious')</script> """)
        good_input = '[".my-class"]'
        with self.assertRaises(Invalid):
            is_valid_json(malicious_input)
        self.assertTrue(is_valid_json(good_input))
