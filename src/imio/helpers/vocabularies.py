# -*- coding: utf-8 -*-

from natsort import humansorted
from operator import attrgetter
from plone import api
from plone.app.vocabularies.users import UsersFactory
from Products.CMFPlone.utils import safe_unicode
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


class SortedUsers(UsersFactory):
    """Append ' (userid)' to term title."""

    def _user_fullname(self, userid):
        """ """
        storage = self.mutable_properties._storage
        data = storage.get(userid, None)
        if data is not None:
            return data.get('fullname', '') or userid
        else:
            return userid

    def __call__(self, context, query=''):
        acl_users = api.portal.get_tool('acl_users')
        self.mutable_properties = acl_users.mutable_properties
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
                    unicode(user_id)
                except UnicodeDecodeError:
                    continue
                term_title = u'{0} ({1})'.format(safe_unicode(
                    self._user_fullname(user_id)), user_id)
                term = SimpleTerm(user_id, user_id, term_title)
                terms.append(term)
        terms = humansorted(terms, key=attrgetter('title'))
        return SimpleVocabulary(terms)


SortedUsersFactory = SortedUsers()
