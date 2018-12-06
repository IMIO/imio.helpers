# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.ZCatalog.ProgressHandler import ZLogHandler
from zope.component import getUtility
from zope.intid.interfaces import IIntIds

import logging


logger = logging.getLogger('imio.helpers:catalog')


class ZCTextIndexInfo:
    '''Silly class used for storing information about a ZCTextIndex.'''
    lexicon_id = 'plone_lexicon'
    index_type = 'Okapi BM25 Rank'


def addOrUpdateIndexes(portal, indexInfos={}):
    '''This method creates or updates, in a p_portal, definitions of indexes
       in its portal_catalog, based on index-related information given in
       p_indexInfos. p_indexInfos is a dictionary of the form
       {s_indexName: (s_indexType, s_indexExtra)}.
       Here are some examples of index types: "FieldIndex", "ZCTextIndex", "DateIndex".'''
    catalog = getToolByName(portal, 'portal_catalog')
    zopeCatalog = catalog._catalog
    addedIndexes = []
    for indexName, indexInfo in indexInfos.iteritems():
        indexType, extra = indexInfo
        if indexType == 'ZCTextIndex' and not extra:
            extra = ZCTextIndexInfo()
        # If this index already exists but with a different type, remove it.
        if indexName in zopeCatalog.indexes:
            storedIndex = zopeCatalog.indexes[indexName]
            oldType = storedIndex.meta_type
            needToDeleteIndex = False
            # if other indexType or changing 'extra' record of a 'ZCTextIndex', remove the index
            if oldType != indexType or \
               (indexType == 'ZCTextIndex' and (storedIndex.lexicon_id != extra.lexicon_id or
                                                storedIndex._index_type != extra.index_type)):
                needToDeleteIndex = True
            if needToDeleteIndex:
                catalog.delIndex(indexName)
                logger.info('Existing index "%s" of type "%s" was removed:'
                            ' we need to recreate it with type "%s".' %
                            (indexName, oldType, indexType))
        if indexName not in zopeCatalog.indexes:
            # We need to create this index
            addedIndexes.append(indexName)
            catalog.addIndex(indexName, indexType, extra)
            logger.info('Created index "%s" of type "%s"...' % (indexName, indexType))

    if addedIndexes:
        pghandler = ZLogHandler()
        catalog.reindexIndex(addedIndexes, portal.REQUEST, pghandler=pghandler)


def removeIndexes(portal, indexes=()):
    '''This method will remove given p_indexes if found in the portal_catalog.'''
    catalog = getToolByName(portal, 'portal_catalog')
    registered_indexes = catalog.indexes()
    for index in indexes:
        if index in registered_indexes:
            catalog.delIndex(index)
            logger.info('Removed index "%s"...' % index)
        else:
            logger.info('Trying to remove an unexisting index with name "%s"...' % index)


def addOrUpdateColumns(portal, columns=()):
    '''This method creates or updates in a p_portal portal_catalog
       the metadata given in p_columns.'''
    catalog = getToolByName(portal, 'portal_catalog')
    addedColumns = []
    for column in columns:
        # Only add it if not already existing
        if column not in catalog.schema():
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


def removeColumns(portal, columns=()):
    '''This method will remove in p_portal portal_catalog
       the metadata given in p_columns.'''
    catalog = getToolByName(portal, 'portal_catalog')
    registered_columns = catalog.schema()
    for column in columns:
        if column in registered_columns:
            catalog.delColumn(column)
            logger.info('Removed column "%s"...' % column)
        else:
            logger.info('Trying to remove an unexisting column with name "%s"...' % column)


def get_intid(obj, intids=None, create=True):
    """ Get intid value or create it if not found """
    if not intids:
        intids = getUtility(IIntIds)
    try:
        return intids.getId(obj)
    except KeyError:
        logger.warn("Missing intid for %s" % obj.absolute_url())
        if create:
            return intids.register(obj)
    return 1
