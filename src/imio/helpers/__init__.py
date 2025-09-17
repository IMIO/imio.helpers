# -*- coding: utf-8 -*-

from datetime import date
from datetime import datetime
from imio.helpers.cache import get_cachekey_volatile
from plone import api
from plone.memoize import ram as pmram
from Products.PlonePAS.plugins.role import GroupAwareRoleManager
from Products.PlonePAS.tools.groups import GroupsTool
from Products.PluggableAuthService.PluggableAuthService import PluggableAuthService
from zope.globalrequest import getRequest
from zope.i18nmessageid import MessageFactory

import logging
import os
import pkg_resources


_ = MessageFactory("imio.helpers")
logger = logging.getLogger("imio.helpers")

HAS_PLONE_4 = api.env.plone_version().startswith("4")
HAS_PLONE_5 = api.env.plone_version().startswith("5")
HAS_PLONE_5_1 = api.env.plone_version() > "5.1"
HAS_PLONE_5_2 = api.env.plone_version() > "5.2"
HAS_PLONE_5_AND_MORE = int(api.env.plone_version()[0]) >= 5
HAS_PLONE_6_AND_MORE = int(api.env.plone_version()[0]) >= 6
PLONE_MAJOR_VERSION = int(api.env.plone_version()[0])

EMPTY_TITLE = "No value"
EMPTY_STRING = "__empty_string__"
EMPTY_DATE = date(1950, 1, 1)
EMPTY_DATETIME = datetime(1950, 1, 1, 12, 0)


try:
    pkg_resources.get_distribution("ftw.labels")
    HAS_FTW_LABELS = True
except pkg_resources.DistributionNotFound:  # pragma: no cover
    HAS_FTW_LABELS = False


if HAS_FTW_LABELS:

    from ftw.labels import indexer as ftw_indexer
    from ftw.labels.interfaces import ILabelSupport
    from plone.indexer.decorator import indexer

    ftw_indexer.__old_labels = ftw_indexer.labels

    @indexer(ILabelSupport)
    def labels(obj):
        original_labels = ftw_indexer.__old_labels(obj)()
        # add EMPTY_STRING if no selected global labels
        # ftw.labels returns ['_'] when no global/personal labels at all
        # personal labels are indexed as ["pers-label", "username:pers-label"]
        pers_labels = [ol.split(':')[1] for ol in original_labels if ':' in ol]
        if original_labels == ['_'] or \
           not [ol for ol in original_labels
                if ':' not in ol and ol not in pers_labels]:
            original_labels.append(EMPTY_STRING)
        return original_labels

    ftw_indexer.labels = labels


def GroupsTool__getGroupsForPrincipal_cachekey(method, self, principal):
    req = getRequest()
    if req is None:
        raise pmram.DontCache
    date = get_cachekey_volatile("_users_groups_value")
    return date, principal and principal.getId()


def GroupAwareRoleManager__getRolesForPrincipal_cachekey(method, self, principal, request=None):
    req = request or getRequest()
    # if req is None:
    #     raise pmram.DontCache
    date = get_cachekey_volatile("_users_groups_value")
    return (
        date,
        principal and principal.getId(),
        repr(req),
        req and (req.get("__ignore_direct_roles__", False), req.get("__ignore_group_roles__", False)) or (None, None),
    )


def PluggableAuthService__getGroupsForPrincipal_cachekey(method, self, principal, request=None, **kwargs):
    req = request or getRequest()
    if req is None:
        raise pmram.DontCache
    try:
        date = get_cachekey_volatile("_users_groups_value")
    except api.portal.CannotGetPortalError:
        raise pmram.DontCache
    return date, principal and principal.getId()


def PluggableAuthService__findUser_cachekey(method, self, plugins, user_id, name=None, request=None):
    req = request or getRequest()
    if req is None:
        raise pmram.DontCache
    try:
        date = get_cachekey_volatile("_users_groups_value")
    except api.portal.CannotGetPortalError:
        raise pmram.DontCache
    return date, repr(plugins), user_id, name, str(req and req._debug or "")


def PluggableAuthService__verifyUser_cachekey(method, self, plugins, user_id=None, login=None):
    req = getRequest()
    if req is None:
        raise pmram.DontCache

    date = get_cachekey_volatile("_users_groups_value")
    return date, repr(plugins), user_id, login


def GroupsTool_getGroupById_cachekey(method, self, group_id):
    req = getRequest()
    if req is None:
        raise pmram.DontCache

    date = get_cachekey_volatile("_users_groups_value")
    return date, group_id


if os.getenv("decorate_acl_methods", "Nope") in ("True", "true"):
    logger.info("DECORATING various acl related methods with cache")
    decorator = pmram.cache(GroupsTool__getGroupsForPrincipal_cachekey)
    GroupsTool.getGroupsForPrincipal = decorator(GroupsTool.getGroupsForPrincipal)
    decorator = pmram.cache(GroupAwareRoleManager__getRolesForPrincipal_cachekey)
    GroupAwareRoleManager.getRolesForPrincipal = decorator(GroupAwareRoleManager.getRolesForPrincipal)
    decorator = pmram.cache(PluggableAuthService__getGroupsForPrincipal_cachekey)
    PluggableAuthService._getGroupsForPrincipal = decorator(PluggableAuthService._getGroupsForPrincipal)
    # decorator = pmram.cache(PluggableAuthService__findUser_cachekey)
    # PluggableAuthService._findUser = decorator(PluggableAuthService._findUser)
    # decorator = pmram.cache(PluggableAuthService__verifyUser_cachekey)
    # PluggableAuthService._verifyUser = decorator(PluggableAuthService._verifyUser)
    decorator = pmram.cache(GroupsTool_getGroupById_cachekey)
    GroupsTool.getGroupById = decorator(GroupsTool.getGroupById)
