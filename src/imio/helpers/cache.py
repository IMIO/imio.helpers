# -*- coding: utf-8 -*-
import logging
from zope.component import getAllUtilitiesRegisteredFor
from zope.component import getUtility
from zope.component import queryUtility
from zope.schema.interfaces import IVocabularyFactory
from plone.memoize.instance import Memojito
from plone.memoize.interfaces import ICacheChooser


logger = logging.getLogger('imio.helpers:cache')


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
