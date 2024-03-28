# -*- coding: utf-8 -*-

from imio.helpers import HAS_PLONE_5_AND_MORE
from imio.helpers.content import add_file
from imio.helpers.content import add_image
from imio.helpers.content import add_to_annotation
from imio.helpers.content import base_getattr
from imio.helpers.content import create
from imio.helpers.content import del_from_annotation
from imio.helpers.content import disable_link_integrity_checks
from imio.helpers.content import get_back_relations
from imio.helpers.content import get_from_annotation
from imio.helpers.content import get_object
from imio.helpers.content import get_relations
from imio.helpers.content import get_schema_fields
from imio.helpers.content import get_user_fullname
from imio.helpers.content import get_vocab
from imio.helpers.content import get_vocab_values
from imio.helpers.content import normalize_name
from imio.helpers.content import object_ids
from imio.helpers.content import object_values
from imio.helpers.content import restore_link_integrity_checks
from imio.helpers.content import richtextval
from imio.helpers.content import safe_delattr
from imio.helpers.content import set_to_annotation
from imio.helpers.content import sort_on_vocab_order
from imio.helpers.content import uuidsToCatalogBrains
from imio.helpers.content import uuidsToObjects
from imio.helpers.content import uuidToCatalogBrain
from imio.helpers.content import uuidToObject
from imio.helpers.content import validate_fields
from imio.helpers.testing import IntegrationTestCase
from imio.helpers.tests.utils import require_module
from imio.helpers.tests.utils import unrequire_module
from plone import api
from plone.app.vocabularies.types import PortalTypesVocabulary
from plone.registry.interfaces import IRegistry
from z3c.relationfield.relation import RelationValue
from zope.annotation import IAnnotations
from zope.component import getUtility
from zope.event import notify
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent import ObjectModifiedEvent
from zope.schema._bootstrapinterfaces import WrongType
from zope.schema.vocabulary import SimpleVocabulary

import os
import six


if HAS_PLONE_5_AND_MORE:
    from Products.CMFPlone.interfaces import IEditingSchema


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
        self.assertEqual(obj, get_object(oid='mydoc'))
        # Give title
        self.assertEqual(obj, get_object(title='My document'))
        # Give type
        self.assertEqual(obj, get_object(ptype='Document', oid='mydoc'))
        # All parameters
        self.assertEqual(obj, get_object(ptype='Document', oid='mydoc', title='My document', parent='folder'))
        self.assertEqual(obj, get_object(ptype='Document', oid='mydoc', title='My document', obj_path='folder/mydoc'))

    def test_add_image(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        obj = api.content.create(container=self.portal.folder, id='tt', type='testingtype')
        if six.PY3:
            barcode_resource = "barcode_python3_zint_60x60_156bytes.png"
        else:
            barcode_resource = "barcode_python2_zint_60x60_278bytes.png"
        add_image(obj, filepath=os.path.join(current_dir, barcode_resource))
        self.assertEqual(obj.image.filename, barcode_resource)
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
        self.assertListEqual([1, 2], list(ret.keys()))
        self.assertIn('folder1', self.portal.folder.objectIds())
        # bad cid format
        conf = [{'cid': 0, 'cont': '/folder', 'type': 'Folder', 'id': 'folder2', 'title': 'Folder2'}]
        with self.assertRaises(ValueError) as cm:
            create(conf)
        if six.PY3:
            self.assertEqual(cm.exception.args[0], "Dict nb 0: cid '0' must be an integer > 0")
            conf = [{'cid': 'bad', 'cont': '/folder', 'type': 'Folder', 'id': 'folder2', 'title': 'Folder2'}]
            with self.assertRaises(ValueError) as cm:
                create(conf)
            self.assertEqual(cm.exception.args[0], "Dict nb 0: cid 'bad' must be an integer > 0")
            # bad container
            conf = [{'cid': 3, 'cont': '/badfolder', 'type': 'Folder', 'id': 'folder2', 'title': 'Folder2'}]
            with self.assertRaises(ValueError) as cm:
                create(conf)
            self.assertEqual(cm.exception.args[0], "Dict nb 0 (cid=3): cannot find container '/badfolder')")
            conf = [{'cid': 3, 'cont': 10, 'type': 'Folder', 'id': 'folder2', 'title': 'Folder2'}]
            with self.assertRaises(ValueError) as cm:
                create(conf)
            self.assertEqual(cm.exception.args[0], "Dict nb 0 (cid=3): cannot find container '10')")
            # cid container
            conf = [{'cid': 3, 'cont': 2, 'type': 'Document', 'id': 'doc1', 'title': 'Doc1'}]
            ret = create(conf, globl=True)
            self.assertIn(3, ret)
            self.assertIn('doc1', self.portal.folder.folder1.objectIds())
            # clean globl
            conf = [{'cid': 4, 'cont': 2, 'type': 'Document', 'id': 'doc2', 'title': 'Doc2'}]
            with self.assertRaises(ValueError) as cm:
                create(conf, globl=True, clean_globl=True)
            self.assertEqual(cm.exception.args[0], "Dict nb 0 (cid=4): cannot find container '2')")
        else:
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
        self.assertListEqual(
            sorted([name for (name, fld) in get_schema_fields(obj=obj, behaviors=False)]),
            sorted(['text', 'enabled', 'mandatory_textline', 'relations', 'textline']))
        self.assertListEqual(
            sorted([name for (name, fld) in get_schema_fields(obj=obj)]),
            sorted(['text', 'enabled', 'mandatory_textline', 'relations', 'textline',
                    'description', 'title', 'title',
                    'tal_condition', 'roles_bypassing_talcondition']))
        self.assertListEqual(
            sorted([name for (name, fld) in get_schema_fields(obj=obj, prefix=True)]),
            sorted(['text', 'enabled', 'mandatory_textline', 'relations', 'textline',
                    'IBasic.description', 'IBasic.title', 'INameFromTitle.title',
                    'ITALCondition.tal_condition', 'ITALCondition.roles_bypassing_talcondition']))
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
        if six.PY3:
            self.assertEqual(validate_fields(obj),
                             [WrongType(None, str, 'mandatory_textline')])
        else:
            self.assertEqual(validate_fields(obj),
                             [WrongType(None, six.text_type, 'mandatory_textline')])
        # validate_fields may raise a ValueError if raise_on_errors=True
        self.assertRaises(ValueError, validate_fields, obj, raise_on_errors=True)
        # back to correct value
        obj.mandatory_textline = u'Some text'
        self.assertFalse(validate_fields(obj))

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
        ret = add_to_annotation('test_annot', 'tralala', uid=obj.UID())
        self.assertEqual(ret, 'tralala')
        self.assertEqual(IAnnotations(obj)['test_annot'], ['tralala'])
        add_to_annotation('test_annot', 'tralala', uid=obj.UID())
        self.assertEqual(IAnnotations(obj)['test_annot'], ['tralala'])
        self.assertEqual(get_from_annotation('test_annot', obj=obj), ['tralala'])
        add_to_annotation('test_annot', 'trilili', obj=obj)
        self.assertEqual(IAnnotations(obj)['test_annot'], ['tralala', 'trilili'])
        # add value with uid that doesn't match an object raises no error.
        ret = add_to_annotation('test_annot', 'tralala', uid='znfzete tztzfozaebfozaefg')
        self.assertIsNone(ret)
        # test remove
        ret = del_from_annotation('test_annot', 'tralala', uid=obj.UID())
        self.assertEqual(ret, 'tralala')
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
        # test simple set
        ret = set_to_annotation('test_annot', 'trululu', obj=obj)
        self.assertEqual(ret, 'trululu')
        self.assertEqual(IAnnotations(obj)['test_annot'], 'trululu')
        set_to_annotation('test_annot', 'trululuid', uid=obj.UID())
        self.assertEqual(IAnnotations(obj)['test_annot'], 'trululuid')
        ret = set_to_annotation('test_annot', 'trululu', uid='df dgf fdsqqe dsf')
        self.assertIsNone(ret)

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

    def test_uuidsToCatalogBrains_query_parameter(self):
        folder = self.portal.folder
        folder2 = self.portal.folder2
        folder_uid = folder.UID()
        folder2_uid = folder2.UID()
        self.assertEqual(api.content.get_state(folder), 'internal')
        api.content.transition(folder2, 'hide')
        self.assertEqual(api.content.get_state(folder2), 'private')
        uuids = [folder_uid, folder2_uid]
        self.assertEqual(len(uuidsToCatalogBrains(uuids)), 2)
        self.assertEqual(len(uuidsToCatalogBrains(uuids, query={'review_state': 'internal'})), 1)

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

    def test_uuidToCatalogBrain(self):
        folder_uid = self.portal.folder.UID()
        single_brain = uuidToCatalogBrain(folder_uid)
        self.assertEqual(single_brain.UID, folder_uid)

    def test_uuidToObject(self):
        folder_uid = self.portal.folder.UID()
        single_obj = uuidToObject(folder_uid)
        self.assertEqual(single_obj.UID(), folder_uid)
        self.assertIsNone(uuidToObject('unknown_uid'))

    def test_disable_link_integrity_checks(self):
        if HAS_PLONE_5_AND_MORE:
            registry = getUtility(IRegistry)
            settings = registry.forInterface(IEditingSchema, prefix="plone")
        else:
            settings = self.portal.portal_properties.site_properties
        self.assertTrue(settings.enable_link_integrity_checks)
        disable_link_integrity_checks()
        self.assertFalse(settings.enable_link_integrity_checks)

    def test_restore_link_integrity_checks(self):
        if HAS_PLONE_5_AND_MORE:
            registry = getUtility(IRegistry)
            settings = registry.forInterface(IEditingSchema, prefix="plone")
        else:
            settings = self.portal.portal_properties.site_properties
        self.assertTrue(settings.enable_link_integrity_checks)
        restore_link_integrity_checks(False)
        self.assertFalse(settings.enable_link_integrity_checks)
        restore_link_integrity_checks(True)
        self.assertTrue(settings.enable_link_integrity_checks)

    def test_get_vocab(self):
        vocab = get_vocab(self.portal, 'plone.app.vocabularies.PortalTypes')
        self.assertTrue(isinstance(vocab, SimpleVocabulary))
        vocab = get_vocab(None, 'plone.app.vocabularies.PortalTypes', only_factory=True)
        self.assertTrue(isinstance(vocab, PortalTypesVocabulary))

    def test_get_vocab_values(self):
        values = get_vocab_values(self.portal, 'plone.app.vocabularies.PortalTypes')
        self.assertTrue("testingtype" in values)
        self.assertTrue("Folder" in values)
        self.assertTrue("Document" in values)
        values = get_vocab_values(self.portal, 'plone.app.vocabularies.PortalTypes', attr_name='value')
        self.assertTrue("testingtype" in values)
        self.assertTrue("Folder" in values)
        self.assertTrue("Document" in values)
        values = get_vocab_values(self.portal, 'plone.app.vocabularies.PortalTypes', attr_name='title')
        self.assertTrue(u"Testing type" in values)
        self.assertTrue(u"Folder" in values)
        self.assertTrue(u"Page" in values)

    def test_safe_delattr(self):
        attr_name = 'testing_attr_name'
        setattr(self.portal, attr_name, attr_name)
        self.assertTrue(hasattr(self.portal, attr_name))
        safe_delattr(self.portal, attr_name)
        self.assertFalse(hasattr(self.portal, attr_name))
        safe_delattr(self.portal, attr_name)
        self.assertFalse(hasattr(self.portal, attr_name))

    def test_get_relations(self):
        obj = api.content.create(container=self.portal.folder, id='tt', type='testingtype')
        intids = getUtility(IIntIds)
        obj.relations = [RelationValue(intids.getId(self.portal.folder))]
        notify(ObjectModifiedEvent(obj))
        self.assertEqual(len(list(get_relations(obj))), 1)
        self.assertEqual(len(list(get_relations(obj, 'relations'))), 1)
        self.assertTrue(isinstance(list(get_relations(obj, 'relations'))[0], RelationValue))
        self.assertEqual(len(list(get_relations(obj, 'unknown'))), 0)
        self.assertTrue(isinstance(list(get_relations(obj, 'relations', as_obj=True))[0],
                                   self.portal.folder.__class__))

    def test_get_back_relations(self):
        obj = api.content.create(container=self.portal.folder, id='tt', type='testingtype')
        intids = getUtility(IIntIds)
        obj.relations = [RelationValue(intids.getId(self.portal.folder))]
        notify(ObjectModifiedEvent(obj))
        self.assertEqual(len(list(get_back_relations(self.portal.folder))), 1)
        self.assertEqual(len(list(get_back_relations(self.portal.folder, 'relations'))), 1)
        self.assertEqual(len(list(get_back_relations(self.portal.folder, 'unknown'))), 0)
        self.assertTrue(isinstance(list(get_back_relations(self.portal.folder, 'relations'))[0], obj.__class__))

    def test_richtextval(self):
        obj1 = api.content.create(container=self.portal.folder, id='tt1', type='testingtype')
        obj2 = api.content.create(container=self.portal.folder, id='tt2', type='testingtype')
        obj1.text = richtextval("<p>My text</p>")
        self.assertEqual(obj1.text.raw, u"<p>My text</p>")
        self.assertEqual(obj1.text.output, u"<p>My text</p>")
        # use safe_html
        text_with_link = '<p>My text <a href="resolveuid/{0}">link</a></p>'.format(obj2.UID())
        obj1.text = richtextval(text_with_link)
        self.assertEqual(obj1.text.raw, text_with_link)
        self.assertEqual(obj1.text.output, u'<p>My text <a href="http://nohost/plone/folder/tt2">link</a></p>')

    def test_normalize_name(self):
        request = self.portal.REQUEST
        self.assertEqual(normalize_name(request, u'CV Informaticien N\xb02016-1'),
                         'cv-informaticien-ndeg2016-1')
        self.assertEqual(normalize_name(request, u'Héhé du texte'),
                         'hehe-du-texte')

    @require_module('Products.Archetypes')
    def test_at_object_values(self):
        self.assertEqual(object_values(self.portal, 'ATFolder'), [self.portal.folder, self.portal.folder2])
        # may pass a list of class names
        self.assertEqual(object_values(self.portal, ['Folder', 'ATFolder']),
                         [self.portal.folder, self.portal.folder2])

    @unrequire_module('Products.Archetypes')
    def test_object_values(self):
        self.assertEqual(object_values(self.portal, 'Folder'), [self.portal.folder, self.portal.folder2])
        # may pass a list of class names
        self.assertEqual(object_values(self.portal, ['Folder', 'ATFolder']),
                         [self.portal.folder, self.portal.folder2])

    @require_module('Products.Archetypes')
    def test_at_object_ids(self):
        self.assertEqual(object_ids(self.portal, 'ATFolder'), ['folder', 'folder2'])
        # may pass a list of class names
        self.assertEqual(object_ids(self.portal, ['Folder', 'ATFolder']),
                         ['folder', 'folder2'])

    @unrequire_module('Products.Archetypes')
    def test_object_ids(self):
        self.assertEqual(object_ids(self.portal, 'Folder'), ['folder', 'folder2'])
        # may pass a list of class names
        self.assertEqual(object_ids(self.portal, ['Folder', 'ATFolder']),
                         ['folder', 'folder2'])

    def test_get_user_fullname(self):
        self.assertIsNone(get_user_fullname(None))
        self.assertEqual(get_user_fullname("unknown_user", none_if_unfound=True), None)
        self.assertEqual(get_user_fullname("unknown_user"), "unknown_user")
        # create some users
        user1 = api.user.create('a@b.be', 'user1', 'secret1234', properties={'fullname': 'Stéphan Smith'})
        api.user.create('a@b.be', 'user2', 'secret1234', properties={'fullname': ''})
        self.assertEqual(get_user_fullname("user1"), u'Stéphan Smith')
        if six.PY3:
            self.assertEqual(user1.getProperty("fullname"), get_user_fullname("user1"))
        else:
            self.assertEqual(user1.getProperty("fullname").decode('utf8'), get_user_fullname("user1"))
        self.assertEqual(get_user_fullname("user2"), u'user2')
        # group
        self.assertEqual(get_user_fullname("Reviewers", none_if_no_user=True), None)
        self.assertEqual(get_user_fullname("Reviewers"), u'Reviewers')
        # with_user_id
        self.assertEqual(get_user_fullname("user1", with_user_id=True), u'Stéphan Smith (user1)')
        self.assertEqual(get_user_fullname("user2", with_user_id=True), u'user2 (user2)')

    def test_base_getattr(self):
        obj = api.content.create(container=self.portal.folder, id='mydoc', type='Document', title='My doc')
        setattr(self.portal.folder, "dedana", True)
        # getattr uses acquisition
        self.assertTrue(getattr(self.portal.folder, 'dedana'))
        self.assertTrue(getattr(obj, 'dedana'))
        # base_getattr does not use acquisition
        self.assertTrue(base_getattr(self.portal.folder, 'dedana'))
        self.assertIsNone(base_getattr(obj, 'dedana'))
        # returns default if given
        self.assertEqual(base_getattr(obj, 'dedana', {}), {})

    def test_sort_on_vocab_order(self):
        self.assertEqual(
            sort_on_vocab_order(('testingtype', 'Link', 'Document', 'File'),
                                vocab_name='plone.app.vocabularies.PortalTypes'),
            ['File', 'Link', 'Document', 'testingtype'])
        vocab = get_vocab(self.portal, 'plone.app.vocabularies.PortalTypes')
        self.assertEqual(
            sort_on_vocab_order(('testingtype', 'Link', 'Document', 'File'),
                                vocab=vocab),
            ['File', 'Link', 'Document', 'testingtype'])
        # not found values are moved to the end
        self.assertEqual(
            sort_on_vocab_order(('testingtype', 'unknown1', 'Link', 'Document', 'File'),
                                vocab=vocab),
            ['File', 'Link', 'Document', 'testingtype', 'unknown1'])
        self.assertEqual(
            sort_on_vocab_order(('testingtype', 'unknown2', 'Link', 'Document', 'File', 'unknown1'),
                                vocab=vocab),
            ['File', 'Link', 'Document', 'testingtype', 'unknown2', 'unknown1'])
