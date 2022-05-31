# -*- coding: utf-8 -*-

from imio.helpers.cache import get_cachekey_volatile
from plone.memoize import ram
from Products.PlonePAS.plugins.role import GroupAwareRoleManager
from Products.PlonePAS.tools.groups import GroupsTool
from Products.PluggableAuthService.PluggableAuthService import PluggableAuthService
from zope.globalrequest import getRequest
from zope.i18nmessageid import MessageFactory


_ = MessageFactory('imio.helpers')


def get_cachekey1(method, self, principal):
    date = get_cachekey_volatile('Products.PloneMeeting.ToolPloneMeeting._users_groups_value')
    return date, principal.id


def get_cachekey2(method, self, principal, request=None):
    date = get_cachekey_volatile('Products.PloneMeeting.ToolPloneMeeting._users_groups_value')
    return date, principal.id


def get_cachekey3(method, self, principal, request=None, **kwargs):
    date = get_cachekey_volatile('Products.PloneMeeting.ToolPloneMeeting._users_groups_value')
    return date, principal.id


def get_cachekey4(method, self, plugins, user_id, name=None, request=None):
    date = get_cachekey_volatile('Products.PloneMeeting.ToolPloneMeeting._users_groups_value')
    req = getRequest()
    return date, repr(plugins), user_id, name, str(req and req._debug or '')


def get_cachekey5(method, self, plugins, user_id=None, login=None):
    date = get_cachekey_volatile('Products.PloneMeeting.ToolPloneMeeting._users_groups_value')
    return date, repr(plugins), user_id, login


def get_cachekey6(method, self, group_id):
    date = get_cachekey_volatile('Products.PloneMeeting.ToolPloneMeeting._users_groups_value')
    return date, group_id


decorator = ram.cache(get_cachekey2)
GroupsTool.getGroupsForPrincipal = decorator(GroupsTool.getGroupsForPrincipal)
decorator = ram.cache(get_cachekey2)
GroupAwareRoleManager.getRolesForPrincipal = decorator(GroupAwareRoleManager.getRolesForPrincipal)
decorator = ram.cache(get_cachekey3)
PluggableAuthService._getGroupsForPrincipal = decorator(PluggableAuthService._getGroupsForPrincipal)
decorator = ram.cache(get_cachekey4)
PluggableAuthService._findUser = decorator(PluggableAuthService._findUser)
decorator = ram.cache(get_cachekey5)
PluggableAuthService._verifyUser = decorator(PluggableAuthService._verifyUser)
decorator = ram.cache(get_cachekey6)
GroupsTool.getGroupById = decorator(GroupsTool.getGroupById)
