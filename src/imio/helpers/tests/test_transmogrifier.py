# -*- coding: utf-8 -*-

from imio.helpers.testing import IntegrationTestCase
from imio.helpers.transmogrifier import get_main_path
from imio.helpers.transmogrifier import relative_path

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
