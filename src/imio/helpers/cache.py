# -*- coding: utf-8 -*-
from datetime import datetime
from persistent.mapping import PersistentMapping
from plone import api
from plone.i18n.normalizer import IIDNormalizer
from plone.memoize import ram
from plone.memoize.forever import _memos
from plone.memoize.instance import Memojito
from plone.memoize.interfaces import ICacheChooser
from Products.CMFPlone.utils import base_hasattr
from types import FunctionType
from zope.component import getAllUtilitiesRegisteredFor
from zope.component import getUtility
from zope.component import queryUtility
from zope.ramcache.interfaces.ram import IRAMCache
from zope.schema.interfaces import IVocabularyFactory

import logging


logger = logging.getLogger('imio.helpers:cache')
VOLATILE_NAME_MAX_LENGTH = 200
VOLATILE_ATTR = '_volatile_cache_keys'
METHODS_MAPPING_NAME = '_methods_invalidation_mapping'


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


def cleanRamCacheFor(methodId):
    """Clean ram.cache for given p_methodId."""
    cache_chooser = getUtility(ICacheChooser)
    thecache = cache_chooser(methodId)
    thecache.ramcache.invalidate(methodId)


def cleanForeverCache():
    """Clean cache using the @forever.memoize decorator."""
    _memos.clear()


def get_cachekey_volatile(name, method=None):
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
    # store caller method path so it will be invalidated in invalidate_cachekey_volatile_for
    if method:
        key = '%s.%s' % (method.__module__, method.__name__)
        methods = volatiles.get(METHODS_MAPPING_NAME)
        if methods is None:
            volatiles[METHODS_MAPPING_NAME] = PersistentMapping()
        if name not in volatiles[METHODS_MAPPING_NAME]:
            volatiles[METHODS_MAPPING_NAME][name] = []
        if key not in volatiles[METHODS_MAPPING_NAME][name]:
            volatiles[METHODS_MAPPING_NAME][name].append(key)
    return date


def invalidate_cachekey_volatile_for(name, get_again=False, invalidate_cache=True):
    """ """
    portal = api.portal.get()
    normalized_name = queryUtility(IIDNormalizer).normalize(
        name, max_length=VOLATILE_NAME_MAX_LENGTH)
    volatile_name = normalized_name
    volatiles = getattr(portal, VOLATILE_ATTR, {})
    if volatile_name in volatiles:
        del volatiles[volatile_name]
    # when the key is invalidated, get_cachekey_volatile so it
    # stores a new date and it avoids a second write
    if get_again:
        get_cachekey_volatile(volatile_name)
    # when date is invalidated, every cache using it is stale
    # so we may either specifically invalidate this cached methods
    # or just wait for ram.cache to do it's cleanup itself
    if invalidate_cache:
        mapping = volatiles.get(METHODS_MAPPING_NAME, {})
        if name in mapping:
            for method in mapping[name]:
                cleanRamCacheFor(method)
            mapping.pop(name)


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


def obj_modified(obj, asdatetime=True, check_annotation=True, asstring=False):
    """Returns max value between obj.modified(), obj._p_mtime and __anotations__._p_mtime.

       to check also attribute modification and annotation modification."""
    if check_annotation and base_hasattr(obj, '__annotations__'):
        modified = max(float(obj.modified()), obj._p_mtime, obj.__annotations__._p_mtime)
    else:
        modified = max(float(obj.modified()), obj._p_mtime)
    if asdatetime:
        modified = datetime.fromtimestamp(modified)
    elif asstring:
        modified = datetime.fromtimestamp(modified).strftime('%Y%m%d-%H%M%S-%f')
    return modified


def extract_wrapped(decorated):
    """Returns function that was decorated"""
    closure = (c.cell_contents for c in decorated.__closure__)
    return next((c for c in closure if isinstance(c, FunctionType)), None)


def setup_ram_cache(max_entries=100000, max_age=2400, cleanup_interval=600):
    """Can be called in IProcessStarting subscriber"""
    ramcache = queryUtility(IRAMCache)
    logger.info('=> Setting ramcache parameters (maxEntries=%s, maxAge=%s, cleanupInterval=%s)' %
                (max_entries, max_age, cleanup_interval))
    ramcache.update(maxEntries=max_entries, maxAge=max_age, cleanupInterval=cleanup_interval)
