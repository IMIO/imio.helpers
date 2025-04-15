# -*- coding: utf-8 -*-

from imio.helpers import HAS_PLONE_4
from imio.helpers.cache import get_cachekey_volatile
from imio.helpers.cache import get_plone_groups_for_user
from imio.helpers.cache import invalidate_cachekey_volatile_for
from plone.api.exc import InvalidParameterError
from plone.memoize import ram
from Products.PlonePAS.plugins.role import GroupAwareRoleManager
from Products.PluggableAuthService.plugins.ZODBRoleManager import ZODBRoleManager
from smtplib import SMTP_SSL
from zope.sendmail.mailer import SMTPMailer

import pkg_resources


try:
    pkg_resources.get_distribution("collective.solr")
except pkg_resources.DistributionNotFound:
    HAS_SOLR = False
else:
    from collective.solr.indexer import SolrIndexProcessor
    HAS_SOLR = True


def solr_index(self, obj, attributes=None):
    # Fix issue https://github.com/collective/collective.solr/issues/189
    if attributes is not None:
        attributes = None
    return SolrIndexProcessor._old_index(self, obj, attributes)


def ssl_makeMailer(self):
    """ Create a SMTPMailer with SMTP_SSL if port is 465 """
    mailer = SMTPMailer(hostname=self.smtp_host, port=int(self.smtp_port), username=self.smtp_uid or None,
                        password=self.smtp_pwd or None, force_tls=self.force_tls)
    if self.smtp_port in (465, '465'):
        mailer.smtp = SMTP_SSL
    return mailer


def assignRolesToPrincipal(self, roles, principal_id, REQUEST=None):  # noqa
    GroupAwareRoleManager._old_assignRolesToPrincipal(self, roles, principal_id, REQUEST)
    # we need to invalidate cachekey
    invalidate_cachekey_volatile_for('_users_groups_value')


def assignRoleToPrincipal(self, role_id, principal_id):
    ZODBRoleManager._old_assignRoleToPrincipal(self, role_id, principal_id)
    # we need to invalidate cachekey
    invalidate_cachekey_volatile_for('_users_groups_value')


def removeRoleFromPrincipal(self, role_id, principal_id):
    ZODBRoleManager._old_removeRoleFromPrincipal(self, role_id, principal_id)
    # we need to invalidate cachekey
    invalidate_cachekey_volatile_for('_users_groups_value')


def _listAllowedRolesAndUsers_cachekey(method, self, user):
    '''cachekey method for self._listAllowedRolesAndUsers.'''
    date = get_cachekey_volatile('_users_groups_value')
    return date, user.getId()


@ram.cache(_listAllowedRolesAndUsers_cachekey)
def _listAllowedRolesAndUsers(self, user):
    """Monkeypatch to use get_plone_groups_for_user instead getGroups.
       Moreover store this in the REQUEST."""
    # Makes sure the list includes the user's groups.
    result = user.getRoles()
    if 'Anonymous' in result:
        # The anonymous user has no further roles
        return ['Anonymous']
    result = list(result)
    # XXX change, replaced getGroups by get_plone_groups_for_user
    # if hasattr(aq_base(user), 'getGroups'):
    #     groups = ['user:%s' % x for x in user.getGroups()]
    try:
        groups = get_plone_groups_for_user(user=user)
    except InvalidParameterError:
        groups = user.getGroups()
    if groups:
        groups = ['user:%s' % x for x in groups]
        result = result + groups
    # Order the arguments from small to large sets
    result.insert(0, 'user:%s' % user.getId())
    result.append('Anonymous')
    return result


if HAS_PLONE_4:
    from operator import attrgetter
    from plone.app.querystring.registryreader import logger
    from zope.component import queryUtility
    from zope.i18n import translate
    from zope.i18nmessageid import Message
    from zope.schema.interfaces import IVocabularyFactory

    def getVocabularyValues(self, values):
        """Get all vocabulary values if a vocabulary is defined"""

        for field in values.get(self.prefix + '.field').values():
            # XXX begin change by imio.helpers
            # field['values'] = {}
            from collections import OrderedDict
            field['values'] = OrderedDict()
            # XXX end change by imio.helpers
            vocabulary = field.get('vocabulary', [])
            if vocabulary:
                utility = queryUtility(IVocabularyFactory, vocabulary)
                if utility is not None:
                    for item in sorted(utility(self.context),
                                       key=attrgetter('title')):
                        if isinstance(item.title, Message):
                            title = translate(item.title, context=self.request)
                        else:
                            title = item.title

                        field['values'][item.value] = {'title': title}
                else:
                    logger.info("%s is missing, ignored." % vocabulary)
        return values
