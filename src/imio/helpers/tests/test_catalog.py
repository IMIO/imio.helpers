# -*- coding: utf-8 -*-

from plone import api

from imio.helpers.testing import IntegrationTestCase
from imio.helpers.catalog import addOrUpdateIndexes
from imio.helpers.catalog import addOrUpdateColumns
from imio.helpers.catalog import ZCTextIndexInfo


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
        self.assertTrue(not 'reversedUID' in self.catalog.indexes())
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
        self.assertTrue(not 'reversedUID' in self.catalog.schema())
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
        self.assertTrue(not 'reversedUID' in self.catalog.schema())
        # add a document prior to adding the index
        api.content.create(type='Document',
                           id='prior-document',
                           container=self.portal)
        addOrUpdateColumns(self.portal, ('reversedUID', ))
        # no corresponding index exists
        self.assertTrue(not 'reversedUID' in self.catalog.indexes())
        # the metadata was actually added
        self.assertTrue('reversedUID' in self.catalog.schema())
        # and existing objects were updated
        brains = self.catalog()
        for brain in brains:
            obj = brain.getObject()
            self.assertTrue(obj.UID()[::-1] == brain.reversedUID)

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
