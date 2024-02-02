# -*- coding: utf-8 -*-

from datetime import datetime
from datetime import timedelta
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
from zope.globalrequest import getRequest
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


def get_cachekey_volatile(name, method=None, ttl=0):
    """Helper for using a volatile corresponding to p_name
       to be used as cachekey stored in a volatile.
       If it exists, we return the value, either we store datetime.now().
       If p_ttl (time to live) is given, a cachekey older that ttl is updated."""
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
    now = datetime.now()
    # compute new date if None or if using ttl and ttl is stale
    if not date or (ttl and date + timedelta(seconds=ttl) < now):
        date = now
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
    # if get_again=True, when the key is invalidated,
    # get_cachekey_volatile so it stores a new date and it avoids a second write
    date = get_cachekey_volatile(volatile_name) if get_again else None
    # when date is invalidated, every cache using it is stale
    # so we may either specifically invalidate this cached methods
    # or just wait for ram.cache to do it's cleanup itself
    if invalidate_cache:
        mapping = volatiles.get(METHODS_MAPPING_NAME, {})
        if name in mapping:
            for method in mapping[name]:
                cleanRamCacheFor(method)
            mapping.pop(name)
    return date


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
    if hasattr(func, 'im_class'):  # unbounded func (no more in py3)
        path.append(func.im_class.__name__)
        path.append(func.__name__)
    elif hasattr(func, '__qualname__'):
        path.append(func.__qualname__)
    else:
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


def obj_modified(obj, asdatetime=True, check_annotation=True):
    """Returns max value between obj.modified(), obj._p_mtime and __anotations__._p_mtime
       to check also attribute modification and annotation modification.
       Returns a float when asdatetime=False.
    """
    modified = max(float(obj.modified()), obj._p_mtime)
    if check_annotation and base_hasattr(obj, '__annotations__'):
        # when stored annotation is a PersistentMapping, we need to check _p_mtime
        # of stored annotation because a change in the PersistentMapping will not change
        # the __annotations__ _p_mtime
        ann_max_time = max(
            [obj.__annotations__._p_mtime] +
            [obj.__annotations__[k]._p_mtime
             for k in obj.__annotations__.keys()
             if hasattr(obj.__annotations__[k], '_p_mtime')])
        modified = max(float(obj.modified()),
                       obj._p_mtime,
                       ann_max_time)
    if asdatetime:
        modified = datetime.fromtimestamp(modified)
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


def get_current_user_id(request=None):
    """Try to get user_id from REQUEST or fallback to plone.api."""
    user_id = None
    try:
        if request is None:
            request = getRequest()
        user_id = request["AUTHENTICATED_USER"].getId()
    except Exception:
        user_id = api.user.get_current().getId()
    return user_id


def get_plone_groups_for_user_cachekey(method, user_id=None, user=None, the_objects=False):
    """cachekey method for self.get_plone_groups_for_user."""
    date = get_cachekey_volatile('_users_groups_value')
    return (date,
            # use user.getId() and not user.id because when user is a PloneUser instance
            # it does not have a "id" and returns "acl_users" which break the invalidation
            user and user.getId() or user_id or get_current_user_id(getRequest()),
            the_objects)


@ram.cache(get_plone_groups_for_user_cachekey)
def get_plone_groups_for_user(user_id=None, user=None, the_objects=False):
    """Just return user.getGroups but cached.
       This method is tested in
       Products.PloneMeeting.tests.testToolPloneMeeting.test_pm_Get_plone_groups_for_user."""
    if api.user.is_anonymous():
        return []
    if user is None:
        user = user_id and api.user.get(user_id) or api.user.get_current()
    if not hasattr(user, "getGroups"):
        return []
    if the_objects:
        pg = api.portal.get_tool("portal_groups")
        user_groups = pg.getGroupsByUserId(user.getId())
    else:
        user_groups = user.getGroups()
    return sorted(user_groups)


def get_users_in_plone_groups_cachekey(method, group_id=None, group=None, the_objects=False):
    """cachekey method for self.get_users_in_plone_groups."""
    date = get_cachekey_volatile('_users_groups_value')
    return (date,
            group and group.getId() or group_id,
            the_objects)


@ram.cache(get_users_in_plone_groups_cachekey)
def get_users_in_plone_groups(group_id=None, group=None, the_objects=False):
    """Just return group.getGroupMembers but cached."""
    if not group and group_id:
        group = api.group.get(group_id)
    if group is None:
        return []
    members = group.getGroupMembers()
    if not the_objects:
        members = [m.getId() for m in members]
    return sorted(members)
