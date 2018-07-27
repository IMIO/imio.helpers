# -*- coding: utf-8 -*-

from imio.helpers.security import generate_password
from imio.helpers.security import get_environment
from imio.helpers.security import is_develop_environment
from imio.helpers.testing import IntegrationTestCase

import os
import re


class TestSecurityModule(IntegrationTestCase):
    """
    Test all helper methods of security module.
    """

    def setUp(self):
        if 'IS_DEV_ENV' in os.environ.keys():
            del os.environ['IS_DEV_ENV']
        if 'ENV' in os.environ.keys():
            del os.environ['ENV']

    def test_is_develop_environment(self):
        os.environ['IS_DEV_ENV'] = 'false'
        self.assertFalse(is_develop_environment())
        os.environ['IS_DEV_ENV'] = 'true'
        self.assertTrue(is_develop_environment())

    def test_get_environment(self):
        os.environ['ENV'] = 'staging'
        self.assertFalse(is_develop_environment())
        self.assertEqual(get_environment(), 'staging')
        os.environ['ENV'] = 'dev'
        self.assertEqual(get_environment(), 'dev')
        self.assertTrue(is_develop_environment())

    def test_generate_password(self):
        pwd = generate_password(length=10, digits=1, upper=1, lower=1, special=1, readable=False)
        self.assertEqual(len(pwd), 10)
        self.assertIsNotNone(re.search(r'\d', pwd))
        self.assertIsNotNone(re.search(r'[A-Z]', pwd))
        self.assertIsNotNone(re.search(r'[a-z]', pwd))
        self.assertIsNotNone(re.search(r'[!#$%&*+<=>?@-]', pwd))
