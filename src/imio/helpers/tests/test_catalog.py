# -*- coding: utf-8 -*-

from imio.helpers.testing import IntegrationTestCase
from imio.helpers.catalog import addOrUpdateIndexes
from imio.helpers.catalog import addOrUpdateColumns
from plone import api


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
        addOrUpdateIndexes(self.portal, {'reversedUID': 'FieldIndex', })
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
        addOrUpdateIndexes(self.portal, {'reversedUID': 'FieldIndex', })
        # the added index type is 'FieldIndex'
        self.assertTrue(self.catalog._catalog.indexes['reversedUID'].meta_type == 'FieldIndex')
        # now add it as a KeyWordIndex
        addOrUpdateIndexes(self.portal, {'reversedUID': 'KeywordIndex', })
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
        addOrUpdateIndexes(self.portal, {'reversedUID': 'FieldIndex', })
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
