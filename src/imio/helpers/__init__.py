# -*- coding: utf-8 -*-

from zope.i18nmessageid import MessageFactory
from zope.globalrequest import getRequest


_ = MessageFactory('imio.helpers')


def get_cachekey1(method, self, principal):
    return principal.id

def get_cachekey2(method, self, principal, plugins, request=None):
    return principal.id

def get_cachekey3(method, self, principal, request=None, **kwargs):
    return principal.id

def get_cachekey4(method, self, plugins, user_id, name=None, request=None):
    return repr(plugins), user_id, name, str(getRequest()._debug)


from Products.PlonePAS.tools.groups import GroupsTool
from Products.PlonePAS.plugins.role import GroupAwareRoleManager
from Products.PluggableAuthService.PluggableAuthService import PluggableAuthService
from plone.memoize import ram

decorator = ram.cache(get_cachekey2)
GroupsTool.getGroupsForPrincipal = decorator(GroupsTool.getGroupsForPrincipal)
decorator = ram.cache(get_cachekey2)
GroupAwareRoleManager.getRolesForPrincipal = decorator(GroupAwareRoleManager.getRolesForPrincipal)
decorator = ram.cache(get_cachekey3)
PluggableAuthService._getGroupsForPrincipal = decorator(PluggableAuthService._getGroupsForPrincipal)
decorator = ram.cache(get_cachekey4)
PluggableAuthService._findUser = decorator(PluggableAuthService._findUser)
