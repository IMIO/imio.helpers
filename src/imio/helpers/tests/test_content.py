# -*- coding: utf-8 -*-

import os
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

    def test_transitions(self):
        self.portal.portal_workflow.setChainForPortalTypes(('Document', ), ('intranet_workflow', ))
        obj = api.content.create(container=self.portal.folder, id='mydoc', type='Document')
        self.assertEqual(api.content.get_state(obj), 'internal')
        # apply one transition
        transitions(obj, 'submit')
        self.assertEqual(api.content.get_state(obj), 'pending')
        # apply multiple transitions
        transitions(obj, ['publish_internally', 'publish_externally'])
        self.assertEqual(api.content.get_state(obj), 'external')
        transitions(obj, ['submit', 'retract', 'hide'])
        self.assertEqual(api.content.get_state(obj), 'private')

    def test_add_image(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        obj = api.content.create(container=self.portal.folder, id='tt', type='testingtype')
        add_image(obj, filepath=os.path.join(current_dir, 'barcode.png'))
        self.assertEqual(obj.image.filename, u'barcode.png')
        obj1 = api.content.create(container=self.portal.folder, id='tt1', type='testingtype')
        add_image(obj1, img_obj=obj)
        self.assertEqual(obj.image, obj1.image)  # same image object

    def test_add_file(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        obj = api.content.create(container=self.portal.folder, id='tt', type='testingtype')
        add_file(obj, filepath=os.path.join(current_dir, 'dot.gif'))
        self.assertEqual(obj.file.filename, u'dot.gif')
        obj1 = api.content.create(container=self.portal.folder, id='tt1', type='testingtype')
        add_file(obj1, file_obj=obj)
        self.assertEqual(obj.file, obj1.file)  # same file object
