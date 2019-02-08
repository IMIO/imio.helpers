# -*- coding: utf-8 -*-
from datetime import datetime
from plone import api
from plone.i18n.normalizer import IIDNormalizer
from plone.memoize import ram
from plone.memoize.instance import Memojito
from plone.memoize.interfaces import ICacheChooser
from zope.component import getAllUtilitiesRegisteredFor
from zope.component import getUtility
from zope.component import queryUtility
from zope.schema.interfaces import IVocabularyFactory
from persistent.mapping import PersistentMapping

import logging


logger = logging.getLogger('imio.helpers:cache')
VOLATILE_NAME_MAX_LENGTH = 200
VOLATILE_ATTR = '_volatile_cache_keys'


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
    volatile_name = normalized_name
    volatiles = getattr(portal, VOLATILE_ATTR, None)
    if volatiles is None:
        portal._volatile_cache_keys = PersistentMapping()
        volatiles = portal._volatile_cache_keys
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
    volatile_name = normalized_name
    volatiles = getattr(portal, VOLATILE_ATTR, {})
    if volatile_name in volatiles:
        del volatiles[volatile_name]


def _generate_params_key(*args, **kwargs):
    items = []
    for item in kwargs.items():
        elements = []
        for i in item:
            if isinstance(i, list):
                i = tuple(i)
            elements.append(i)
        items.append(tuple(elements))
    return (args, frozenset(items))


def generate_key(func):
    """Return the complete path for a function e.g. module.function"""
    if hasattr(func, '_cache_key'):
        return func._cache_key
    path = [func.__module__]
    if hasattr(func, 'im_class'):
        path.append(func.im_class.__name__)
    path.append(func.__name__)
    return '.'.join(path)


def volatile_cache_with_parameters(func):

    def get_key(func, *args, **kwargs):
        return (
            get_cachekey_volatile(generate_key(func)),
            _generate_params_key(*args, **kwargs),
        )

    def cache(get_key):
        return ram.cache(get_key)

    replacement = cache(get_key)(func)
    replacement._cache_key = generate_key(func)
    return replacement


def volatile_cache_without_parameters(func):

    def get_key(func, *args, **kwargs):
        return (
            get_cachekey_volatile(generate_key(func)),
            (),
        )

    def cache(get_key):
        return ram.cache(get_key)

    replacement = cache(get_key)(func)
    replacement._cache_key = generate_key(func)
    return replacement
