# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
import logging

logger = logging.getLogger('imio.helpers:catalog')


class ZCTextIndexInfo:
    '''Silly class used for storing information about a ZCTextIndex.'''
    lexicon_id = "plone_lexicon"
    index_type = 'Okapi BM25 Rank'


def addOrUpdateIndexes(portal, indexInfos={}):
    '''This method creates or updates, in a p_portal, definitions of indexes
       in its portal_catalog, based on index-related information given in
       p_indexInfo. p_indexInfo is a dictionary of the form
       {s_indexName:s_indexType}. Here are some examples of index types:
       "FieldIndex", "ZCTextIndex", "DateIndex".
       p_metadataInfo is a list of metadata to create from given p_indexInfo.'''
    catalog = getToolByName(portal, 'portal_catalog')
    zopeCatalog = catalog._catalog
    for indexName, indexType in indexInfos.iteritems():
        # If this index already exists but with a different type, remove it.
        if (indexName in zopeCatalog.indexes):
            oldType = zopeCatalog.indexes[indexName].__class__.__name__
            if oldType != indexType:
                catalog.delIndex(indexName)
                logger.info('Existing index "%s" of type "%s" was removed:'
                            ' we need to recreate it with type "%s".' %
                            (indexName, oldType, indexType))
        addedIndexes = []
        if indexName not in zopeCatalog.indexes:
            # We need to create this index
            addedIndexes.append(indexName)
            if indexType != 'ZCTextIndex':
                catalog.addIndex(indexName, indexType)
            else:
                catalog.addIndex(indexName, indexType, extra=ZCTextIndexInfo)
            logger.info('Created index "%s" of type "%s"...' % (indexName, indexType))

    if addedIndexes:
        # Indexing database content based on this index.
        catalog.reindexIndex(addedIndexes, portal.REQUEST)


def addOrUpdateColumns(portal, columnInfos=()):
    '''This method creates or updates, in a p_portal, definitions of metadata
       defined in given p_metadataInfos.'''
    catalog = getToolByName(portal, 'portal_catalog')
    addedColumns = []
    for column in columnInfos:
        # Only add it if not already existing
        if not column in catalog.schema():
            addedColumns.append(column)
            catalog.addColumn(column)
            logger.info('Added metadata "%s"...' % column)

    if addedColumns:
        # update relevant metadata
        # there is no helper method in ZCatalog to update metadata
        # we need to get every catalogued objects and call reindexObject
        paths = catalog._catalog.uids.keys()
        for path in paths:
            obj = catalog.resolve_path(path)
            if obj is None:
                logger.error('Could not update metadata for an object from the uid %r.' % path)
            else:
                obj.reindexObject(idxs=addedColumns)
