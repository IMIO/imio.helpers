# -*- coding: utf-8 -*-

from collections import OrderedDict
from imio.helpers import HAS_PLONE_5_AND_MORE
from imio.helpers.catalog import addOrUpdateColumns
from imio.helpers.catalog import addOrUpdateIndexes
from imio.helpers.catalog import get_intid
from imio.helpers.catalog import merge_queries
from imio.helpers.catalog import reindexIndexes
from imio.helpers.catalog import removeColumns
from imio.helpers.catalog import removeIndexes
from imio.helpers.catalog import ZCTextIndexInfo
from imio.helpers.testing import IntegrationTestCase
from plone import api
from plone.app.testing import applyProfile
from zope.component import getUtility
from zope.intid.interfaces import IIntIds

import six


class TestCatalogModule(IntegrationTestCase):
    """
    Test all helper methods of catalog module.
    """

    def test_addOrUpdateIndexes(self):
        """
        Normal usecase of addOrUpdateIndexes, this will add a new index of required type.
        Moreover existing objects will be updated.
        """
        # for now reversedUID index does not exist...
        self.assertTrue('reversedUID' not in self.catalog.indexes())
        # add a document prior to adding the index
        priorDocument = api.content.create(type='Document',
                                           id='prior-document',
                                           container=self.portal)
        addOrUpdateIndexes(self.portal, {'reversedUID': ('FieldIndex', {})})
        self.assertTrue('reversedUID' in self.portal.portal_catalog.indexes())
        # moreover existing objects were updated
        brains = self.catalog(reversedUID=priorDocument.UID()[::-1])
        self.assertTrue(len(brains) == 1)
        self.assertTrue(brains[0].getObject().UID() == priorDocument.UID())

    def test_addOrUpdateSeveralIndexes(self):
        """
        It is possible to pass several new indexes to addOrUpdateIndexes,
        in this case, only new indexes are added and updated.
        """
        # for now reversedUID index does not exist...
        self.assertTrue('reversedUID' not in self.catalog.indexes())
        # and add an existing index UID
        if HAS_PLONE_5_AND_MORE:
            tagname = self.catalog.Indexes['UID'].__class__.__name__
        else:
            tagname = self.catalog.Indexes['UID'].getTagName()
        self.assertTrue(tagname == 'UUIDIndex')
        # add a document prior to adding the index
        priorDocument = api.content.create(type='Document',
                                           id='prior-document',
                                           container=self.portal)
        addOrUpdateIndexes(
            self.portal,
            # use an ordered dict so UID, an existing index, is after the new one
            OrderedDict([
                ('reversedUID', ('FieldIndex', {})),
                ('UID', ('UUIDIndex', {}))])
        )
        self.assertTrue('reversedUID' in self.portal.portal_catalog.indexes())
        # moreover existing objects were updated
        brains = self.catalog(reversedUID=priorDocument.UID()[::-1])
        self.assertTrue(len(brains) == 1)
        self.assertTrue(brains[0].getObject().UID() == priorDocument.UID())

    def test_updateIndexType(self):
        """
        If an index already exists with a given type, it can be updated
        to another given type.  Add an index of type 'FieldIndex' then
        turn it into a 'KeywordIndex'.
        """
        addOrUpdateIndexes(self.portal, {'reversedUID': ('FieldIndex', {})})
        # the added index type is 'FieldIndex'
        self.assertTrue(self.catalog._catalog.indexes['reversedUID'].meta_type == 'FieldIndex')
        # now add it as a KeyWordIndex
        addOrUpdateIndexes(self.portal, {'reversedUID': ('KeywordIndex', {})})
        self.assertTrue(self.catalog._catalog.indexes['reversedUID'].meta_type == 'KeywordIndex')

    def test_addOrUpdateColumnsWithExistingIndex(self):
        """
        Normal usecase of addOrUpdateColumns, this will add a new column (metadata).
        Test here when a corresponding index exists.
        Moreover existing objects will be updated.
        """
        # for now reversedUID metadata does not exist...
        self.assertTrue('reversedUID' not in self.catalog.schema())
        # add a document prior to adding the index
        api.content.create(type='Document',
                           id='prior-document',
                           container=self.portal)
        addOrUpdateIndexes(self.portal, {'reversedUID': ('FieldIndex', {})})
        addOrUpdateColumns(self.portal, ('reversedUID', ))
        # the metadata was actually added
        self.assertTrue('reversedUID' in self.catalog.schema())
        # and existing objects were updated
        brains = self.catalog()
        for brain in brains:
            obj = brain.getObject()
            self.assertTrue(obj.UID()[::-1] == brain.reversedUID)

    def test_addOrUpdateColumnsWithoutExistingIndex(self):
        """
        Usecase of addOrUpdateColumns, this will add a new column (metadata).
        Test here when a no corresponding index exists.
        Moreover existing objects will be updated.
        """
        # for now reversedUID metadata does not exist...
        self.assertTrue('reversedUID' not in self.catalog.schema())
        # add a document prior to adding the index
        api.content.create(type='Document',
                           id='prior-document',
                           container=self.portal)
        addOrUpdateColumns(self.portal, ('reversedUID', ))
        # no corresponding index exists
        self.assertTrue('reversedUID' not in self.catalog.indexes())
        # the metadata was actually added
        self.assertTrue('reversedUID' in self.catalog.schema())
        # and existing objects were updated
        brains = self.catalog()
        for brain in brains:
            obj = brain.getObject()
            self.assertTrue(obj.UID()[::-1] == brain.reversedUID)

    def test_addOrUpdateColumnsUnexistingUid(self):
        """
        In case we update the catalog and an uid is still in catalog but object
        does not exist anymore, it does not fail and simply print a message
        in the Zope log.
        """
        # insert an unexisting uid and addOrUpdateColumns
        catalog = self.portal.portal_catalog
        catalog._catalog.uids.insert('/plone/unknown', 123456789)
        self.assertTrue('/plone/unknown' in list(catalog._catalog.uids.keys()))
        addOrUpdateColumns(self.portal, ('new_metadata', ))
        self.assertIsNone(addOrUpdateColumns(self.portal, ('Title', )))

    def test_addOrUpdateZCTextIndex(self):
        """
        While adding a ZCTextIndex, optional 'extra' record can be passed.
        If nothing available, default values are used.
        """
        addOrUpdateIndexes(self.portal, {'sample_zctextindex': ('ZCTextIndex', {})})
        index = self.catalog._catalog.indexes['sample_zctextindex']
        # if no 'extra' record given, default values are used
        self.assertTrue(index.lexicon_id == ZCTextIndexInfo.lexicon_id)
        self.assertTrue(index._index_type == ZCTextIndexInfo.index_type)
        # we can also update an existing ZCTextIndex index
        indexInfos = ZCTextIndexInfo()
        indexInfos.lexicon_id = 'plaintext_lexicon'
        indexInfos.index_type = 'Cosine Measure'
        addOrUpdateIndexes(self.portal, {'sample_zctextindex': ('ZCTextIndex', indexInfos)})
        index = self.catalog._catalog.indexes['sample_zctextindex']
        self.assertTrue(index.lexicon_id == indexInfos.lexicon_id)
        self.assertTrue(index._index_type == indexInfos.index_type)
        # we can change the indexType
        addOrUpdateIndexes(self.portal, {'sample_zctextindex': ('FieldIndex', {})})
        self.assertTrue(self.catalog._catalog.indexes['sample_zctextindex'].meta_type == 'FieldIndex')
        # and back to a ZCTextIndex
        addOrUpdateIndexes(self.portal, {'sample_zctextindex': ('ZCTextIndex', {})})
        self.assertTrue(self.catalog._catalog.indexes['sample_zctextindex'].meta_type == 'ZCTextIndex')

    def test_removeIndexes(self):
        """
        Normal usecase of removeIndexes, this will remove given indexes
        and will not fail even if the index does not exist.
        """
        # remove an existing index, it will only remove the index, not column if also exists
        self.assertTrue('Description' in self.catalog.indexes())
        self.assertTrue('Description' in self.catalog.schema())
        removeIndexes(self.portal, indexes=('Description', ))
        self.assertTrue('Description' not in self.catalog.indexes())
        # the metadata with same name still exists
        self.assertTrue('Description' in self.catalog.schema())
        # if we try to remove an unexisting index, it does not fail
        removeIndexes(self.portal, indexes=('Description', ))

    def test_removeColumns(self):
        """
        Normal usecase of removeColumns, this will remove given colmuns
        and will not fail even if the column does not exist.
        """
        # remove an existing column, it will only remove the column, not the index if also exists
        self.assertTrue('Description' in self.catalog.schema())
        self.assertTrue('Description' in self.catalog.indexes())
        removeColumns(self.portal, columns=('Description', ))
        self.assertTrue('Description' not in self.catalog.schema())
        # the index with same name still exists
        self.assertTrue('Description' in self.catalog.indexes())
        # if we try to remove an unexisting column, it does not fail
        removeColumns(self.portal, columns=('Description', ))

    def test_get_intid(self):
        obj = api.content.create(container=self.portal.folder, id='tt', type='testingtype')
        applyProfile(self.portal, 'plone.app.intid:default')
        intids = getUtility(IIntIds)
        obj_id = intids.getId(obj)
        self.assertEqual(get_intid(obj), obj_id)
        self.assertEqual(get_intid(obj, intids=intids), obj_id)
        intids.unregister(obj)
        self.assertEqual(get_intid(obj, intids=intids, create=False), 1)
        new_id = get_intid(obj, intids=intids)
        self.assertNotEqual(new_id, obj_id)
        self.assertNotEqual(new_id, 1)

    def test_reindexIndexes(self):
        self.assertFalse(self.portal.portal_catalog(Title='specific'))
        obj = api.content.create(container=self.portal.folder, id='tt', type='testingtype', title='other')
        obj.title = 'specific'
        if six.PY3:
            # that it with Plone52py3 / Plone6py3
            self.assertTrue(self.portal.portal_catalog(Title='specific'))
        else:
            self.assertFalse(self.portal.portal_catalog(Title='specific'))
        reindexIndexes(self.portal, ['Title'])
        res = self.portal.portal_catalog(Title='specific')
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].UID, obj.UID())

    def test_merge_queries(self):
        query1 = {'portal_type': {'query': 'Document'}, 'review_state': {'query': ['private']}, }
        query2 = {'portal_type': {'query': ['Document']}, 'review_state': {'query': ['published']}, }
        query3 = {'portal_type': {'query': ['Folder']}, 'Title': {'query': ['title']}, }
        query4 = {'review_state': {'query': 'pending'}}
        query5 = {'Creator': {'query': 'author'}}
        self.assertEqual(merge_queries([query1, query2]),
                         {'portal_type': {'query': ['Document']},
                          'review_state': {'query': ['private', 'published']}})
        self.assertEqual(merge_queries([query1, query3]),
                         {'portal_type': {'query': ['Document', 'Folder']},
                          'review_state': {'query': ['private', 'published']},
                          'Title': {'query': ['title']}})
        self.assertEqual(merge_queries([query2, query4]),
                         {'portal_type': {'query': ['Document']},
                          'review_state': {'query': ['published', 'pending']}})
        self.assertEqual(merge_queries([query1, query2, query3, query4, query5]),
                         {'portal_type': {'query': ['Document', 'Folder']},
                          'Creator': {'query': ['author']},
                          'review_state': {'query': ['private', 'published', 'pending']},
                          'Title': {'query': ['title']}})
