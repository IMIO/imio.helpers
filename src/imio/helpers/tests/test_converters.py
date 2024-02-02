# -*- coding: utf-8 -*-

from imio.helpers import HAS_PLONE_5_AND_MORE
from imio.helpers.testing import IntegrationTestCase
from unittest import makeSuite
from unittest import TestSuite
from ZPublisher.tests.testHTTPRequest import HTTPRequestTests

import html
import imio.helpers.converters  # noqa


class TestConverters(IntegrationTestCase, HTTPRequestTests):

    def test_imiohelpers_json_converter(self):
        inputs = (
            ('data:json', '{"key1": "value1", "key2": "value2"}'),
            ('data2:json', '{"key3": "value3", "key4": "value4"}'), )
        req = self._processInputs(inputs)
        self.assertEqual(req.form,
                         {'data': {u'key2': u'value2', u'key1': u'value1'},
                          'data2': {u'key3': u'value3', u'key4': u'value4'}})

    def test_imiohelpers_json_converter_wrong_format(self):
        # missing " after value1
        inputs = (
            ('data:json', '{"key1": "value1, "key2": "value2"}'), )
        with self.assertRaises(ValueError) as cm:
            self._processInputs(inputs)
        error_message = 'Invalid json \'{"key1": "value1, "key2": "value2"}\''
        if HAS_PLONE_5_AND_MORE:
            self.assertEqual(html.unescape(cm.exception.args[0]), error_message)
        else:
            self.assertEqual(cm.exception.message, error_message)


def test_suite():
    suite = TestSuite()
    # change prefix to avoid executing every tests of HTTPRequestTests
    suite.addTest(makeSuite(TestConverters, prefix='test_imiohelpers_'))
    return suite
