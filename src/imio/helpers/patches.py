# -*- coding: utf-8 -*-
from imio.helpers.cache import invalidate_cachekey_volatile_for
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
