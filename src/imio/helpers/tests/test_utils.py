# -*- coding: utf-8 -*-


from imio.helpers.content import add_file
from imio.helpers.testing import IntegrationTestCase
from imio.helpers.utils import is_pdf
from imio.helpers.utils import is_valid_json
from plone import api
from Products.CMFPlone.utils import safe_unicode
from zope.interface import Invalid

import os


class TestUtils(IntegrationTestCase):

    def test_valid_json(self):
        malicious_input = safe_unicode(""" ""};<script>alert('I'm malicious')</script> """)
        good_input = '[".my-class"]'
        with self.assertRaises(Invalid):
            is_valid_json(malicious_input)
        self.assertTrue(is_valid_json(good_input))

    def test_is_pdf(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        obj = api.content.create(container=self.portal.folder, id="tt", type="testingtype")
        add_file(obj, filepath=os.path.join(current_dir, "dot.gif"))
        self.assertFalse(is_pdf(obj))
        add_file(obj, filepath=os.path.join(current_dir, "file.pdf"))
        self.assertTrue(is_pdf(obj))
