# -*- coding: utf-8 -*-
from imio.helpers.testing import IntegrationTestCase
from imio.helpers.transmogrifier import correct_path
from imio.helpers.transmogrifier import filter_keys
from imio.helpers.transmogrifier import get_main_path
from imio.helpers.transmogrifier import pool_tuples
from imio.helpers.transmogrifier import relative_path
from imio.helpers.transmogrifier import text_to_bool

import os


class TestTesting(IntegrationTestCase):

    def test_correct_path(self):
        self.assertEquals(correct_path(self.portal, 'abcde'), 'abcde')
        self.assertIn('folder', self.portal.objectIds())
        self.assertEquals(correct_path(self.portal, 'folder'), 'folder-1')
        self.assertEquals(correct_path(self.portal, 'folder/abcde'), 'folder/abcde')
        self.portal.folder.invokeFactory('Document', id='abcde', title='Document')
        self.assertEquals(correct_path(self.portal, 'folder/abcde'), 'folder/abcde-1')
        self.portal.folder.invokeFactory('Document', id='abcde-1', title='Document')
        self.assertEquals(correct_path(self.portal, 'folder/abcde'), 'folder/abcde-2')

    def test_filter_keys(self):
        dic = {'a': 1, 'b': 2, 'c': 3}
        self.assertListEqual(['a', 'b', 'c'], sorted(filter_keys(dic, []).keys()))
        self.assertListEqual([1, 2, 3], sorted(filter_keys(dic, []).values()))
        self.assertListEqual(['a', 'b', 'c'], sorted(filter_keys(dic, ['a', 'b', 'c']).keys()))
        self.assertListEqual([1, 2, 3], sorted(filter_keys(dic, ['a', 'b', 'c']).values()))
        self.assertListEqual(['a', 'c'], sorted(filter_keys(dic, ['a', 'c']).keys()))
        self.assertListEqual([1, 3], sorted(filter_keys(dic, ['a', 'c']).values()))

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

    def test_pool_tuples(self):
        lst = [1, 2, 3, 4, 5, 6]
        self.assertListEqual(pool_tuples(lst, 1), [(1,), (2,), (3,), (4,), (5,), (6,)])
        self.assertListEqual(pool_tuples(lst, 2), [(1, 2), (3, 4), (5, 6)])
        self.assertListEqual(pool_tuples(lst, 3), [(1, 2, 3), (4, 5, 6)])
        self.assertListEqual(pool_tuples(lst, 4), [(1, 2, 3, 4)])
        self.assertListEqual(pool_tuples(lst, 6), [(1, 2, 3, 4, 5, 6)])

    def test_relative_path(self):
        self.assertEquals(relative_path(self.portal, '/plone/directory'), 'directory')
        self.assertEquals(relative_path(self.portal, '/alone/directory'), '/alone/directory')

    def test_text_to_bool(self):
        dic = {'True': 'True', 'true': 'true', 'False': 'False', 'false': 'false',
               '0': '0', 0: 0, '1': '1', 123: 123,
               'a': 'a', 'errors': 0}

        def logger(item, msg):
            item['errors'] += 1

        self.assertTrue(text_to_bool(dic, 'True', logger))
        self.assertTrue(text_to_bool(dic, 'true', logger))
        self.assertFalse(text_to_bool(dic, 'False', logger))
        self.assertFalse(text_to_bool(dic, 'false', logger))
        self.assertFalse(text_to_bool(dic, '0', logger))  # using fake log method to test error
        self.assertFalse(text_to_bool(dic, 0, logger))
        self.assertTrue(text_to_bool(dic, '1', logger))
        self.assertTrue(text_to_bool(dic, 123, logger))
        self.assertEquals(dic['errors'], 0)
        self.assertFalse(text_to_bool(dic, 'a', logger))
        self.assertEquals(dic['errors'], 1)
