# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from zope.component import getAllUtilitiesRegisteredFor
from zope.component import getUtility
from zope.component import queryUtility
from zope.schema.interfaces import IVocabularyFactory
from plone import api
from plone.i18n.normalizer import IIDNormalizer
from plone.memoize.instance import Memojito
from plone.memoize.interfaces import ICacheChooser


logger = logging.getLogger('imio.helpers:cache')
VOLATILE_NAME_MAX_LENGTH = 200


def cleanVocabularyCacheFor(vocabulary=None):
    """Clean _memojito_ attribute for given p_vocabulary name.
       If p_vocabulary is None, it will clean every vocabulary _memojito_ attribute."""

    # we received a vocabulary name, just clean this one
    if vocabulary:
        vocabularies = (queryUtility(IVocabularyFactory, vocabulary), )
    else:
        # clean every vocabularies having a _memojito_ attribute
        vocabularies = getAllUtilitiesRegisteredFor(IVocabularyFactory)

    for vocab in vocabularies:
        if hasattr(vocab, Memojito.propname):
            getattr(vocab, Memojito.propname).clear()


def cleanRamCache():
    """Clean the entire ram.cache."""
    cache_chooser = getUtility(ICacheChooser)
    thecache = cache_chooser('')
    thecache.ramcache.invalidateAll()


def cleanRamCacheFor(methodId, obj=None):
    """Clean ram.cache for given p_methodId."""
    cache_chooser = getUtility(ICacheChooser)
    thecache = cache_chooser(methodId)
    thecache.ramcache.invalidate(methodId)


def get_cachekey_volatile(name):
    """Helper for using a volatile corresponding to p_name
       to be used as cachekey stored in a volatile.
       If it exists, we return the value, either we store datetime.now()."""
    portal = api.portal.get()
    # use max_length of VOLATILE_NAME_MAX_LENGTH to avoid cropped names
    # that could lead to having 2 names beginning with same part using same volatile...
    normalized_name = queryUtility(IIDNormalizer).normalize(
        name, max_length=VOLATILE_NAME_MAX_LENGTH)
    volatile_name = '_v_{0}'.format(normalized_name)
    if not hasattr(portal, '_v_cache_keys'):
        portal._v_cache_keys = {}
    volatiles = portal._v_cache_keys
    date = volatiles.get(volatile_name)
    if not date:
        date = datetime.now()
        volatiles[volatile_name] = date
    return date


def invalidate_cachekey_volatile_for(name):
    """ """
    portal = api.portal.get()
    normalized_name = queryUtility(IIDNormalizer).normalize(
        name, max_length=VOLATILE_NAME_MAX_LENGTH)
    volatile_name = '_v_{0}'.format(normalized_name)
    volatiles = getattr(portal, '_v_cache_keys', {})
    if volatile_name in volatiles:
        del volatiles[volatile_name]
