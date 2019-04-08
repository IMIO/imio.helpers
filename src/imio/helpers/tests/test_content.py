# -*- coding: utf-8 -*-

from imio.helpers.content import add_file
from imio.helpers.content import add_image
from imio.helpers.content import add_to_annotation
from imio.helpers.content import create
from imio.helpers.content import del_from_annotation
from imio.helpers.content import disable_link_integrity_checks
from imio.helpers.content import get_from_annotation
from imio.helpers.content import get_object
from imio.helpers.content import get_schema_fields
from imio.helpers.content import restore_link_integrity_checks
from imio.helpers.content import safe_encode
from imio.helpers.content import transitions
from imio.helpers.content import uuidsToCatalogBrains
from imio.helpers.content import uuidsToObjects
from imio.helpers.content import validate_fields
from imio.helpers.testing import IntegrationTestCase
from plone import api
from zope.annotation import IAnnotations
from zope.schema._bootstrapinterfaces import WrongType

import os


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
        self.assertEqual(self.portal, get_object(obj_path='/'))

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

    def test_create(self):
        # no parameter
        conf = [{'cid': 1, 'cont': '/folder', 'type': 'Document', 'id': 'doc1', 'title': 'Doc1'}]
        ret = create(conf)
        self.assertIn(1, ret)
        self.assertIn('doc1', self.portal.folder.objectIds())
        # cids & globl parameters
        conf = [{'cid': 2, 'cont': '/folder', 'type': 'Folder', 'id': 'folder1', 'title': 'Folder1'}]
        ret = create(conf, cids=ret, globl=True)
        self.assertListEqual([1, 2], ret.keys())
        self.assertIn('folder1', self.portal.folder.objectIds())
        # bad cid format
        conf = [{'cid': 0, 'cont': '/folder', 'type': 'Folder', 'id': 'folder2', 'title': 'Folder2'}]
        with self.assertRaises(ValueError) as cm:
            create(conf)
        self.assertEqual(cm.exception.message, "Dict nb 0: cid '0' must be an integer > 0")
        conf = [{'cid': 'bad', 'cont': '/folder', 'type': 'Folder', 'id': 'folder2', 'title': 'Folder2'}]
        with self.assertRaises(ValueError) as cm:
            create(conf)
        self.assertEqual(cm.exception.message, "Dict nb 0: cid 'bad' must be an integer > 0")
        # bad container
        conf = [{'cid': 3, 'cont': '/badfolder', 'type': 'Folder', 'id': 'folder2', 'title': 'Folder2'}]
        with self.assertRaises(ValueError) as cm:
            create(conf)
        self.assertEqual(cm.exception.message, "Dict nb 0 (cid=3): cannot find container '/badfolder')")
        conf = [{'cid': 3, 'cont': 10, 'type': 'Folder', 'id': 'folder2', 'title': 'Folder2'}]
        with self.assertRaises(ValueError) as cm:
            create(conf)
        self.assertEqual(cm.exception.message, "Dict nb 0 (cid=3): cannot find container '10')")
        # cid container
        conf = [{'cid': 3, 'cont': 2, 'type': 'Document', 'id': 'doc1', 'title': 'Doc1'}]
        ret = create(conf, globl=True)
        self.assertIn(3, ret)
        self.assertIn('doc1', self.portal.folder.folder1.objectIds())
        # clean globl
        conf = [{'cid': 4, 'cont': 2, 'type': 'Document', 'id': 'doc2', 'title': 'Doc2'}]
        with self.assertRaises(ValueError) as cm:
            create(conf, globl=True, clean_globl=True)
        self.assertEqual(cm.exception.message, "Dict nb 0 (cid=4): cannot find container '2')")
        # pos param
        conf = [{'cid': 4, 'cont': 10, 'type': 'Document', 'id': 'doc2', 'title': 'The first element'}]
        ret = create(conf, cids={10: self.portal.folder}, pos=True)
        self.assertIn(4, ret)
        self.assertIn('doc2', self.portal.folder.objectIds())
        self.assertEquals(self.portal.folder.getObjectPosition('doc2'), 0)

    def test_get_schema_fields(self):
        """ """
        obj = api.content.create(container=self.portal.folder,
                                 id='tt',
                                 type='testingtype',
                                 enabled='Should be a boolean')
        self.assertListEqual([name for (name, fld) in get_schema_fields(obj=obj, behaviors=False)],
                             ['text', 'enabled', 'mandatory_textline', 'textline'])
        self.assertListEqual([name for (name, fld) in get_schema_fields(obj=obj)],
                             ['text', 'enabled', 'mandatory_textline', 'textline',
                              'description', 'title', 'title',
                              'tal_condition', 'roles_bypassing_talcondition'])
        self.assertListEqual([name for (name, fld) in get_schema_fields(type_name='portnawak')],
                             [])

    def test_validate_fields(self):
        """ """
        obj = api.content.create(container=self.portal.folder,
                                 id='tt',
                                 type='testingtype',
                                 enabled='Should be a boolean',
                                 textline=None,
                                 mandatory_textline=u'Some text',
                                 tal_condition=u'',
                                 roles_bypassing_talcondition=set())
        self.assertEqual(validate_fields(obj),
                         [WrongType('Should be a boolean', bool, 'enabled')])
        obj.enabled = False
        self.assertFalse(validate_fields(obj))
        obj.enabled = True
        self.assertFalse(validate_fields(obj))
        # not required fields other than Bool must contain something
        # else than None if field is required=True
        obj.mandatory_textline = None
        self.assertEqual(validate_fields(obj),
                         [WrongType(None, unicode, 'mandatory_textline')])
        # validate_fields may raise a ValueError if raise_on_errors=True
        self.assertRaises(ValueError, validate_fields, obj, raise_on_errors=True)
        # back to correct value
        obj.mandatory_textline = u'Some text'
        self.assertFalse(validate_fields(obj))

    def test_safe_encode(self):
        self.assertEqual(safe_encode('héhé'), 'héhé')
        self.assertEqual(safe_encode(u'héhé'), 'héhé')
        self.assertEqual(safe_encode(u'héhé', encoding='utf8'), 'héhé')
        self.assertEqual(safe_encode('héhé', encoding='whatelse'), 'héhé')

    def test_add_and_remove_annotation(self):
        obj = api.content.create(container=self.portal.folder,
                                 id='tt',
                                 type='testingtype',
                                 enabled='Should be a boolean')
        fakeUid = obj.UID()
        api.content.delete(obj)
        obj = api.content.create(container=self.portal.folder,
                                 id='tt',
                                 type='testingtype',
                                 enabled='Should be a boolean')
        # test get
        self.assertIsNone(get_from_annotation('test_annot', obj=obj))
        self.assertEqual(get_from_annotation('test_annot', obj=obj, default='empty'), 'empty')
        # get value with uid that doesn't match an object raises no error.
        self.assertEqual(get_from_annotation('test_annot', uid=fakeUid, default='empty'), 'empty')
        # test add
        add_to_annotation('test_annot', 'tralala', uid=obj.UID())
        self.assertEqual(IAnnotations(obj)['test_annot'], ['tralala'])
        add_to_annotation('test_annot', 'tralala', uid=obj.UID())
        self.assertEqual(IAnnotations(obj)['test_annot'], ['tralala'])
        self.assertEqual(get_from_annotation('test_annot', obj=obj), ['tralala'])
        add_to_annotation('test_annot', 'trilili', obj=obj)
        self.assertEqual(IAnnotations(obj)['test_annot'], ['tralala', 'trilili'])
        # add value with uid that doesn't match an object raises no error.
        add_to_annotation('test_annot', 'tralala', uid='znfzete tztzfozaebfozaefg')
        # test remove
        del_from_annotation('test_annot', 'tralala', uid=obj.UID())
        self.assertEqual(IAnnotations(obj)['test_annot'], ['trilili'])
        del_from_annotation('test_annot', 'trilili', uid=obj.UID())
        self.assertEqual(IAnnotations(obj)['test_annot'], [])
        # remove value with uid that doesn't match an object raises no error.
        del_from_annotation('test_annot', 'tralala', uid=fakeUid)
        # remove value that doesn't exist in set
        del_from_annotation('test_annot', 'trololo', uid=obj.UID())
        self.assertEqual(IAnnotations(obj)['test_annot'], [])
        # remove value from a no-existing key in annotation
        self.assertIsNone(del_from_annotation('test_not_key_in_annot', 'trololo', uid=obj.UID()))

    def test_uuidsToCatalogBrains(self):
        folder_uid = self.portal.folder.UID()
        folder2_uid = self.portal.folder2.UID()
        uuids = [folder_uid, folder2_uid]
        self.assertEqual(len(uuidsToCatalogBrains(uuids)), 2)
        uuids = [folder_uid, folder2_uid, 'unknown_uid']
        self.assertEqual(len(uuidsToCatalogBrains(uuids)), 2)
        self.assertEqual(
            [brain.UID for brain in uuidsToCatalogBrains(uuids, ordered=True)],
            [folder_uid, folder2_uid])
        uuids = [folder2_uid, folder_uid]
        self.assertEqual(
            [brain.UID for brain in uuidsToCatalogBrains(uuids, ordered=True)],
            uuids)

    def test_uuidsToObjects(self):
        folder_uid = self.portal.folder.UID()
        folder2_uid = self.portal.folder2.UID()
        uuids = [folder_uid, folder2_uid, 'unknown_uid']
        self.assertEqual(len(uuidsToObjects(uuids)), 2)
        self.assertEqual(
            uuidsToObjects(uuids, ordered=True),
            [self.portal.folder, self.portal.folder2])
        uuids = [folder2_uid, folder_uid]
        self.assertEqual(
            uuidsToObjects(uuids, ordered=True),
            [self.portal.folder2, self.portal.folder])

    def test_disable_link_integrity_checks(self):
        self.assertTrue(self.portal.portal_properties.site_properties.enable_link_integrity_checks)
        disable_link_integrity_checks()
        self.assertFalse(self.portal.portal_properties.site_properties.enable_link_integrity_checks)

    def test_restore_link_integrity_checks(self):
        self.assertTrue(self.portal.portal_properties.site_properties.enable_link_integrity_checks)
        restore_link_integrity_checks(False)
        self.assertFalse(self.portal.portal_properties.site_properties.enable_link_integrity_checks)
        restore_link_integrity_checks(True)
        self.assertTrue(self.portal.portal_properties.site_properties.enable_link_integrity_checks)
