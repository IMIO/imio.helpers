# -*- coding: utf-8 -*-

from imio.helpers.testing import IntegrationTestCase
from imio.helpers.transmogrifier import get_main_path
from imio.helpers.transmogrifier import relative_path
from imio.helpers.transmogrifier import text_int_to_bool

import os


class TestTesting(IntegrationTestCase):

    def test_get_main_path(self):
        orig_home = os.getenv('INSTANCE_HOME')
        orig_pwd = os.getenv('PWD')
        self.assertEquals(get_main_path('/etc'), '/etc')
        os.environ['INSTANCE_HOME'] = '/etc/parts/xx'
        self.assertEquals(get_main_path(), '/etc')
        os.environ['INSTANCE_HOME'] = '/etc/abcd'
        os.environ['PWD'] = '/myhome'
        self.assertRaisesRegexp(Exception, u"Path '/myhome' doesn't exist", get_main_path)  # path doesn't exist
        self.assertRaisesRegexp(Exception, u"Path '/myhome/toto' doesn't exist", get_main_path, subpath='toto')
        self.assertEquals(get_main_path('/', 'etc'), '/etc')
        os.environ['INSTANCE_HOME'] = orig_home
        os.environ['PWD'] = orig_pwd

    def test_relative_path(self):
        self.assertEquals(relative_path(self.portal, '/plone/directory'), 'directory')
        self.assertEquals(relative_path(self.portal, '/alone/directory'), '/alone/directory')

    def test_text_int_to_bool(self):
        dic = {'0': '0', 0: 0, '1': '1', 123: 123, 'a': 'a', 'errors': 0}

        def logger(item, msg):
            item['errors'] += 1

        self.assertFalse(text_int_to_bool(dic, '0', logger))  # using fake log method to test error
        self.assertFalse(text_int_to_bool(dic, 0, logger))
        self.assertTrue(text_int_to_bool(dic, '1', logger))
        self.assertTrue(text_int_to_bool(dic, 123, logger))
        self.assertEquals(dic['errors'], 0)
        self.assertFalse(text_int_to_bool(dic, 'a', logger))
        self.assertEquals(dic['errors'], 1)
