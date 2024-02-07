# -*- coding: utf-8 -*-

from imio.helpers import get_cachekey_volatile
from imio.helpers.content import get_user_fullname
from natsort import humansorted
from operator import attrgetter
from plone import api
from plone.memoize import ram
from Products.CMFPlone.utils import safe_unicode
from zope.i18n import translate
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

import six


try:
    from plone.app.vocabularies.principals import UsersFactory  # Plone6
except ImportError:
    from plone.app.vocabularies.users import UsersFactory


def voc_cache_key(method, self, context=None, query=''):
    """Returns a persistent portal stored date following the given cache key.

    Must be programatically invalidated."""
    return get_cachekey_volatile('_users_groups_value')


def get_users_voc(with_userid):
    acl_users = api.portal.get_tool('acl_users')
    users = acl_users.searchUsers(sort_by='')
    terms = []
    # manage duplicates, this can be the case when using LDAP and same userid in source_users
    userids = []
    for user in users:
        user_id = user['id']
        if user_id not in userids:
            userids.append(user_id)
            # bypass special characters, may happen when using LDAP
            try:
                six.text_type(user_id)
            except UnicodeDecodeError:
                continue
            if with_userid:
                term_title = u'{0} ({1})'.format(get_user_fullname(user_id), user_id)
            else:
                term_title = get_user_fullname(user_id)
            term = SimpleTerm(user_id, user_id, term_title)
            terms.append(term)
    terms = humansorted(terms, key=attrgetter('title'))
    return SimpleVocabulary(terms)


class SortedUsers(UsersFactory):
    """Create a users vocabulary with userid as value.
    Append ' (userid)' to term title."""

    @ram.cache(voc_cache_key)
    def SortedUsers__call__(self, context=None, query=''):
        return get_users_voc(True)

    __call__ = SortedUsers__call__


SortedUsersFactory = SortedUsers()


class SimplySortedUsers(SortedUsers):
    """With userid as value and fullname as title"""

    @ram.cache(voc_cache_key)
    def SimplySortedUsers__call__(self, context=None, query=''):
        return get_users_voc(False)

    __call__ = SimplySortedUsers__call__


SimplySortedUsersFactory = SimplySortedUsers()


class EnhancedTerm(SimpleTerm):

    def __init__(self, value, token=None, title=None, **attrs):
        super(EnhancedTerm, self).__init__(value, token=token, title=title)
        self.attrs = attrs


@implementer(IVocabularyFactory)
class YesNoForFacetedVocabulary(object):
    """Vocabulary to be used with a faceted radio widget on a field index containing prefixed 0 and 1 strings."""

    prefix = ''

    def __call__(self, context):
        """ """
        res = [
            SimpleTerm(self.prefix + '0', self.prefix + '0',
                       safe_unicode(translate('yesno_value_false', domain='imio.helpers', context=context.REQUEST))),
            SimpleTerm(self.prefix + '1', self.prefix + '1',
                       safe_unicode(translate('yesno_value_true', domain='imio.helpers', context=context.REQUEST)))
        ]
        return SimpleVocabulary(res)
