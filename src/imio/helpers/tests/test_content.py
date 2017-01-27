# -*- coding: utf-8 -*-

from plone import api

from imio.helpers.testing import IntegrationTestCase
from imio.helpers.content import add_file, add_image, create, get_object, richtextval, transitions


class TestContentModule(IntegrationTestCase):
    """
    Test all helper methods of content module.
    """

    def setUp(self):
        self.portal = self.layer['portal']

    def test_get_object(self):
        obj = api.content.create(container=self.portal.folder, id='mydoc', title='My document', type='Document')
        # Give parent information
        self.assertEqual(obj, get_object(parent=self.portal.folder))
        self.assertEqual(obj, get_object(parent='/folder'))
        self.assertEqual(obj, get_object(parent='/folder/'))
        self.assertEqual(obj, get_object(parent='folder/'))
        self.assertEqual(obj, get_object(parent='folder'))
        # Give obj path information
        self.assertEqual(obj, get_object(obj_path='/folder/mydoc'))
        self.assertEqual(obj, get_object(obj_path='/folder/mydoc/'))
        self.assertEqual(obj, get_object(obj_path='folder/mydoc'))
        self.assertEqual(obj, get_object(obj_path='/folder/mydoc', parent='folder'))
        # Give id
        self.assertEqual(obj, get_object(id='mydoc'))
        # Give title
        self.assertEqual(obj, get_object(title='My document'))
        # Give type
        self.assertEqual(obj, get_object(type='Document', id='mydoc'))
        # All parameters
        self.assertEqual(obj, get_object(type='Document', id='mydoc', title='My document', parent='folder'))
        self.assertEqual(obj, get_object(type='Document', id='mydoc', title='My document', obj_path='folder/mydoc'))
