# -*- coding: utf-8 -*-

from datetime import datetime
from imio.helpers.cache import _generate_params_key
from imio.helpers.cache import cleanForeverCache
from imio.helpers.cache import cleanRamCache
from imio.helpers.cache import cleanRamCacheFor
from imio.helpers.cache import cleanVocabularyCacheFor
from imio.helpers.cache import generate_key
from imio.helpers.cache import get_cachekey_volatile
from imio.helpers.cache import invalidate_cachekey_volatile_for
from imio.helpers.cache import obj_modified
from imio.helpers.cache import VOLATILE_ATTR
from imio.helpers.cache import volatile_cache_with_parameters
from imio.helpers.cache import volatile_cache_without_parameters
from imio.helpers.testing import FunctionalTestCase
from imio.helpers.testing import IntegrationTestCase
from persistent.mapping import PersistentMapping
from plone import api
from plone.app.testing import login
from plone.app.testing import logout
from plone.memoize import forever
from plone.memoize import ram
from plone.memoize.instance import Memojito
from plone.memoize.interfaces import ICacheChooser
from Products.CMFCore.utils import _getAuthenticatedUser
from Products.PlonePAS.plugins.ufactory import PloneUser
from zope.annotation import IAnnotations
from zope.component import getUtility
from zope.component import queryUtility
from zope.ramcache.interfaces.ram import IRAMCache
from zope.schema.interfaces import IVocabularyFactory

import os
import time
import transaction


memPropName = Memojito.propname


class Foo(object):

    def bar(self):
        pass


def ramCachedMethod_cachekey(method, portal, param, pass_volatile_method=False):
    '''cachekey method for ramCachedMethod.'''
    # used for test_get_cachekey_volatile_method_cleanup
    if pass_volatile_method:
        date = get_cachekey_volatile('test_cache.ramCachedMethod', method)
    else:
        date = get_cachekey_volatile('test_cache.ramCachedMethod')
    return date, param


@ram.cache(ramCachedMethod_cachekey)
def ramCachedMethod(portal, param, pass_volatile_method=False):
    """ """
    return portal.REQUEST.get('ramcached', None)


@volatile_cache_without_parameters
def volatile_without_parameters_cached(portal):
    return portal.REQUEST.get('volatile_without_parameters_cached', None)


@volatile_cache_with_parameters
def volatile_with_parameters_cached(portal, param):
    return portal.REQUEST.get('volatile_with_parameters_cached', None)


@forever.memoize
def forever_cached_date():
    return datetime.now()


class TestCacheModule(IntegrationTestCase):
    """
    Test all helper methods of cache module.
    """

    def test_cleanVocabularyCacheFor(self):
        """
        This helper method cleans instance.memoize cache defined on a vocabulary.
        """
        self.request.set('vocab_values', ('1', '2'))
        vocab = queryUtility(IVocabularyFactory,
                             "imio.helpers.testing.testingvocabulary")
        # not cached for now
        self.assertFalse(getattr(vocab, memPropName, {}))
        # once get, it is cached
        vocab(self.portal)
        self.assertTrue(getattr(vocab, memPropName))
        self.assertEquals([term.token for term in vocab(self.portal)._terms],
                          ['1', '2'])

        # change value but do not clean cache
        self.request.set('vocab_values', ('1', '2', '3'))
        self.assertEquals([term.token for term in vocab(self.portal)._terms],
                          ['1', '2'])
        # clean vocabulary cache
        cleanVocabularyCacheFor("imio.helpers.testing.testingvocabulary")
        self.assertEquals([term.token for term in vocab(self.portal)._terms],
                          ['1', '2', '3'])

        # every existing vocabularies can also be cleaned if nothing passed to cleanVocabularyCacheFor
        self.request.set('vocab_values', ('1', '2', '3', '4'))
        self.assertEquals([term.token for term in vocab(self.portal)._terms],
                          ['1', '2', '3'])
        # clean vocabulary cache
        cleanVocabularyCacheFor("imio.helpers.testing.testingvocabulary")
        self.assertEquals([term.token for term in vocab(self.portal)._terms],
                          ['1', '2', '3', '4'])

        # if cleanVocabularyCacheFor is called without parameter,
        # every registered vocabularies cache is cleaned
        self.request.set('vocab_values', ('1', '2', '3', '4', '5'))
        self.assertEquals([term.token for term in vocab(self.portal)._terms],
                          ['1', '2', '3', '4'])
        cleanVocabularyCacheFor()
        self.assertEquals([term.token for term in vocab(self.portal)._terms],
                          ['1', '2', '3', '4', '5'])

    def test_cleanRamCache(self):
        """
        This helper method invalidates all ram.cache.
        """
        self.request.set('ramcached', 'a')
        self.assertEquals(ramCachedMethod(self.portal, param='1'), 'a')
        # change value in REQUEST, as it is ram cached, it will still return 'a'
        self.request.set('ramcached', 'b')
        self.assertEquals(ramCachedMethod(self.portal, param='1'), 'a')
        # ram.cache works as expected if param changes
        self.assertEquals(ramCachedMethod(self.portal, param='2'), 'b')
        # try again
        self.assertEquals(ramCachedMethod(self.portal, param='1'), 'a')
        # now clean all caches, it will returns 'b'
        cleanRamCache()
        self.assertEquals(ramCachedMethod(self.portal, param='1'), 'b')

    def test_cleanRamCacheFor(self):
        """
        This helper method invalidates ram.cache for given method.
        """
        self.request.set('ramcached', 'a')
        self.assertEquals(ramCachedMethod(self.portal, param='1'), 'a')
        # change value in REQUEST, as it is ram cached, it will still return 'a'
        self.request.set('ramcached', 'b')
        self.assertEquals(ramCachedMethod(self.portal, param='1'), 'a')
        # ram.cache works as expected if param changes
        self.assertEquals(ramCachedMethod(self.portal, param='2'), 'b')
        # try again
        self.assertEquals(ramCachedMethod(self.portal, param='1'), 'a')
        # now clean cache, it will returns 'b'
        cleanRamCacheFor('imio.helpers.tests.test_cache.ramCachedMethod')
        self.assertEquals(ramCachedMethod(self.portal, param='1'), 'b')

    def test_cleanForeverCache(self):
        """Test the cache.cleanForeverCache function."""
        date = forever_cached_date()
        self.assertEqual(date, forever_cached_date())
        cleanForeverCache()
        new_date = forever_cached_date()
        self.assertNotEqual(date, new_date)
        self.assertEqual(new_date, forever_cached_date())

    def test_get_cachekey_volatile(self):
        """Helper method that adds a volatile on the portal storing current date."""
        method_name = 'My method'
        plone_utils = api.portal.get_tool('plone_utils')
        normalized_name = plone_utils.normalizeString(method_name)
        volatile_name = normalized_name
        self.assertIsNone(getattr(self.portal, volatile_name, None))
        # calling the method will set the volatile on the portal
        date = get_cachekey_volatile(method_name)
        self.assertTrue(isinstance(date, datetime))
        volatiles = getattr(self.portal, VOLATILE_ATTR, {})
        self.assertTrue(isinstance(volatiles.get(volatile_name), datetime))
        # calling it again will still return same date
        self.assertEquals(date, get_cachekey_volatile(method_name))
        # volatiles are not removed by tearDown, remove it now to avoid
        # test isolation issues with test test_invalidate_cachekey_volatile_for
        invalidate_cachekey_volatile_for(method_name)

    def test_get_cachekey_volatile_method(self):
        """Test behavior when method is passed to get_cachekey_volatile."""
        cache_chooser = getUtility(ICacheChooser)
        thecache = cache_chooser("")
        cache_data = thecache.ramcache._getStorage()._data
        # will initialize cachekey_volatile and pass method
        ramCachedMethod(self.portal, param='1', pass_volatile_method=True)
        self.assertTrue('imio.helpers.tests.test_cache.ramCachedMethod' in cache_data)
        volatiles = getattr(self.portal, VOLATILE_ATTR, {})
        self.assertTrue(volatiles["_methods_invalidation_mapping"]["test_cache.ramCachedMethod"])
        # when invalidating cache, the method is cleaned from ramcache
        invalidate_cachekey_volatile_for('test_cache.ramCachedMethod')
        self.assertFalse('imio.helpers.tests.test_cache.ramCachedMethod' in cache_data)
        self.assertEqual(volatiles["_methods_invalidation_mapping"], PersistentMapping())
        # if not passing method to get_cachekey_volatile then cache will not be cleanedup
        ramCachedMethod(self.portal, param='1', pass_volatile_method=False)
        self.assertTrue('imio.helpers.tests.test_cache.ramCachedMethod' in cache_data)
        invalidate_cachekey_volatile_for('test_cache.ramCachedMethod')
        # no cleanup, method still in cache storage
        self.assertTrue('imio.helpers.tests.test_cache.ramCachedMethod' in cache_data)

    def test_get_cachekey_volatile_ttl(self):
        """Check use of parameter "ttl"."""
        date = get_cachekey_volatile("method")
        time.sleep(2)
        self.assertEqual(date, get_cachekey_volatile("method"))
        self.assertNotEqual(date, get_cachekey_volatile("method", ttl=1))

    def test_invalidate_cachekey_volatile_for(self):
        """Helper method that will invalidate a given volatile."""
        method_name = 'My method'
        plone_utils = api.portal.get_tool('plone_utils')
        normalized_name = plone_utils.normalizeString(method_name)
        volatile_name = normalized_name
        self.assertIsNone(getattr(self.portal, volatile_name, None))
        # calling the method if volatile does not exist does not break
        invalidate_cachekey_volatile_for(method_name)
        # set it now
        first_date = get_cachekey_volatile(method_name)
        self.assertTrue(isinstance(first_date, datetime))
        invalidate_cachekey_volatile_for(method_name)
        self.assertIsNone(getattr(self.portal, volatile_name, None))
        # if get_cachekey_volatile is called and volatile does not exist,
        # it is created with datetime.now()
        second_date = get_cachekey_volatile(method_name)
        self.assertTrue(first_date < second_date)
        # when get_again=True, a new date is computed
        new_date = invalidate_cachekey_volatile_for(method_name, get_again=True)
        self.assertEqual(new_date, get_cachekey_volatile(method_name))

    def test_generate_params_key(self):
        """Test _generate_params_key function"""
        self.assertEqual(
            ((1, ), frozenset([('a', 2)])),
            _generate_params_key(1, a=2),
        )
        self.assertEqual(
            ((1, 2), frozenset([('a', 2), ('b', ())])),
            _generate_params_key(1, 2, a=2, b=[]),
        )

    def test_generate_key(self):
        """Test generate_key function"""
        self.assertEqual(
            'imio.helpers.cache.generate_key',
            generate_key(generate_key),
        )

        self.assertEqual(
            'imio.helpers.tests.test_cache.Foo.bar',
            generate_key(Foo.bar),
        )

    def test_volatile_cache_without_parameters(self):
        """Helper cache @volatile_cache_without_parameters"""
        generate_key(volatile_without_parameters_cached)
        self.request.set('volatile_without_parameters_cached', 'a')
        self.assertEqual('a', volatile_without_parameters_cached(self.portal))
        self.request.set('volatile_without_parameters_cached', 'b')
        self.assertEqual('a', volatile_without_parameters_cached(self.portal))
        # Test invalidation
        invalidate_cachekey_volatile_for(
            generate_key(volatile_without_parameters_cached),
        )
        self.assertEqual('b', volatile_without_parameters_cached(self.portal))

    def test_volatile_cache_with_parameters(self):
        """Helper cache @volatile_cache_with_parameters"""
        self.request.set('volatile_with_parameters_cached', 'a')
        self.assertEqual(
            'a',
            volatile_with_parameters_cached(self.portal, 'a'),
        )
        self.request.set('volatile_with_parameters_cached', 'b')
        self.assertEqual(
            'a',
            volatile_with_parameters_cached(self.portal, 'a'),
        )
        self.assertEqual(
            'b',
            volatile_with_parameters_cached(self.portal, 'b'),
        )
        self.request.set('volatile_with_parameters_cached', 'c')
        self.assertEqual(
            'b',
            volatile_with_parameters_cached(self.portal, 'b'),
        )
        # Test invalidation
        invalidate_cachekey_volatile_for(
            generate_key(volatile_with_parameters_cached),
        )
        self.assertEqual(
            'c',
            volatile_with_parameters_cached(self.portal, 'a'),
        )
        self.assertEqual(
            'c',
            volatile_with_parameters_cached(self.portal, 'b'),
        )


class TestCacheModuleFunctional(FunctionalTestCase):
    """
    Test all helper methods of cache module (commits allowed in functional layer).
    """

    def test_obj_modified(self):
        """ """
        # init annotations
        folder = self.portal.folder
        ann = IAnnotations(folder)
        ann['test'] = 0
        transaction.commit()
        ann = folder.__annotations__
        modified = obj_modified(folder)
        # changed when modified
        folder.notifyModified()
        modified2 = obj_modified(folder)
        self.assertNotEqual(modified, modified2)
        # changed when annotation changed
        ann['test'] = 1
        transaction.commit()
        modified3 = obj_modified(folder)
        self.assertNotEqual(modified2, modified3)
        # also working when stored annotation is a dict and something changed into it
        ann['test2'] = PersistentMapping({'key': 'value1'})
        transaction.commit()
        modified4 = obj_modified(folder)
        self.assertNotEqual(modified3, modified4)
        ann['test2']['key'] = 'value2'
        transaction.commit()
        modified5 = obj_modified(folder)
        self.assertNotEqual(modified4, modified5)
        # by default result is a datetime, can be float
        self.assertEqual(type(obj_modified(folder)), datetime)
        self.assertEqual(type(obj_modified(folder, asdatetime=False)), float)


class TestCachedMethods(IntegrationTestCase):
    """
    Test methods that have been dynamically cached in __init__.
    """

    def setUp(self):
        super(TestCachedMethods, self).setUp()
        self.acl = self.portal['acl_users']
        api.user.create('a@b.be', 'user1', '123-45@6U78', properties={'fullname': 'Stéphan Smith'})  # Returns MemberData
        self.user = self.acl.getUserById('user1')  # Returns PloneUser

    def test_getGroupsForPrincipal(self):
        self.skipTest('Temporary skipped')
        pgr = self.portal['portal_groups']
        self.assertListEqual(pgr.getGroupsForPrincipal(self.user),
                             ['AuthenticatedUsers'])
        pgr.addPrincipalToGroup('user1', 'Administrators')
        self.assertListEqual(pgr.getGroupsForPrincipal(self.user),
                             ['Administrators', 'AuthenticatedUsers'])
        api.group.add_user(groupname='Reviewers', user=self.user)
        self.assertListEqual(pgr.getGroupsForPrincipal(self.user),
                             ['Administrators', 'Reviewers', 'AuthenticatedUsers'])
        api.group.remove_user(groupname='Administrators', user=self.user)
        self.assertListEqual(pgr.getGroupsForPrincipal(self.user),
                             ['Reviewers', 'AuthenticatedUsers'])
        pgr.removePrincipalFromGroup('user1', 'Reviewers')
        self.assertListEqual(pgr.getGroupsForPrincipal(self.user),
                             ['AuthenticatedUsers'])

    def test_getRolesForPrincipal(self):
        self.assertIn(os.getenv('decorate_acl_methods', 'Nope'), ('True', 'true'))
        prm = self.acl['portal_role_manager']
        self.assertTupleEqual(prm.getRolesForPrincipal(self.user),
                              ('Member',))
        prm.assignRolesToPrincipal(('Member', 'Reviewer',), 'user1')
        sorted_roles = tuple(sorted(prm.getRolesForPrincipal(self.user), key=str.lower))
        self.assertTupleEqual(sorted_roles,
                              ('Member', 'Reviewer'))
        prm.assignRoleToPrincipal('Contributor', 'user1')
        sorted_roles = tuple(sorted(prm.getRolesForPrincipal(self.user), key=str.lower))
        self.assertTupleEqual(sorted_roles,
                              ('Contributor', 'Member', 'Reviewer'))
        prm.removeRoleFromPrincipal('Reviewer', 'user1')
        sorted_roles = tuple(sorted(prm.getRolesForPrincipal(self.user), key=str.lower))
        self.assertTupleEqual(sorted_roles,
                              ('Contributor', 'Member'))

    def test__getGroupsForPrincipal(self):
        self.skipTest('Temporary skipped')
        pgr = self.portal['portal_groups']
        self.assertListEqual(self.acl._getGroupsForPrincipal(self.user),
                             ['AuthenticatedUsers'])
        pgr.addPrincipalToGroup('user1', 'Administrators')
        self.assertListEqual(self.acl._getGroupsForPrincipal(self.user),
                             ['Administrators', 'AuthenticatedUsers'])
        api.group.add_user(groupname='Reviewers', user=self.user)
        invalidate_cachekey_volatile_for('_users_groups_value', get_again=True)
        self.assertListEqual(self.acl._getGroupsForPrincipal(self.user),
                             ['Administrators', 'Reviewers', 'AuthenticatedUsers'])
        api.group.remove_user(groupname='Administrators', user=self.user)
        self.assertListEqual(self.acl._getGroupsForPrincipal(self.user),
                             ['Reviewers', 'AuthenticatedUsers'])
        pgr.removePrincipalFromGroup('user1', 'Reviewers')
        self.assertListEqual(self.acl._getGroupsForPrincipal(self.user),
                             ['AuthenticatedUsers'])

    def test_imio_global_cache(self):
        from zope.ramcache.ram import caches
        caches.clear()
        ramcache = queryUtility(IRAMCache)
        self.assertEqual(ramcache.getStatistics(), ())
        ramCachedMethod(self.portal, param='1', pass_volatile_method=True)
        stats = ramcache.getStatistics()
        self.assertEqual(len(stats), 1)
        self.assertEqual(stats[0]['path'], 'imio.helpers.tests.test_cache.ramCachedMethod')
        self.assertEqual(stats[0]['hits'], 0)
        self.assertTrue('older_date' in stats[0])
        # hit again
        ramCachedMethod(self.portal, param='1', pass_volatile_method=True)
        stats = ramcache.getStatistics()
        self.assertEqual(len(stats), 1)
        self.assertEqual(stats[0]['path'], 'imio.helpers.tests.test_cache.ramCachedMethod')
        self.assertEqual(stats[0]['hits'], 1)
        self.assertTrue('older_date' in stats[0])

    def test__users_groups_value_invalidation(self):
        """Invalidated whenever any operation on user:
           - user created;
           - user modified;
           - user deleted;
           - user added to group;
           - user removed from group;
           - group created;
           - group removed."""
        value1 = get_cachekey_volatile('_users_groups_value')
        # create user
        user = api.user.create(username='new_user', email='test@test.be')
        value2 = get_cachekey_volatile('_users_groups_value')
        self.assertNotEqual(value1, value2)
        # modify user
        user.setMemberProperties({'email': 'test2@test.be'})
        value3 = get_cachekey_volatile('_users_groups_value')
        self.assertNotEqual(value2, value3)
        # create group
        group = api.group.create('new_group')
        value4 = get_cachekey_volatile('_users_groups_value')
        self.assertNotEqual(value3, value4)
        # modify group, WILL NOT BE INVALIDATED
        group.setGroupProperties({'title': 'Group title'})
        value5 = get_cachekey_volatile('_users_groups_value')
        self.assertEqual(value4, value5)
        # add user to group
        api.group.add_user(group=group, user=user)
        value6 = get_cachekey_volatile('_users_groups_value')
        self.assertNotEqual(value5, value6)
        # remove user from group
        api.group.remove_user(group=group, user=user)
        value7 = get_cachekey_volatile('_users_groups_value')
        self.assertNotEqual(value6, value7)
        # delete user
        api.user.delete(user=user)
        value8 = get_cachekey_volatile('_users_groups_value')
        self.assertNotEqual(value7, value8)
        # delete group
        api.group.delete(group=group)
        value9 = get_cachekey_volatile('_users_groups_value')
        self.assertNotEqual(value8, value9)

    def test__listAllowedRolesAndUsers(self):
        pgr = self.portal['portal_groups']
        new_user = api.user.create(username='new_user', email='test@test.be')
        self.assertEqual(
            self.catalog._listAllowedRolesAndUsers(new_user),
            ['user:new_user', 'Member', 'Authenticated',
             'user:AuthenticatedUsers', 'Anonymous'])
        pgr.addPrincipalToGroup(new_user.getId(), 'Administrators')
        # get again, as we use "getGroups", it is stored on user instance
        new_user = api.user.get(new_user.getId())
        self.assertListEqual(
            sorted(self.catalog._listAllowedRolesAndUsers(new_user)),
            ['Anonymous', 'Authenticated', 'Manager', 'Member', 'user:Administrators', 'user:AuthenticatedUsers',
             'user:new_user'])
        # behaves correctly with a PloneUser because of id/getId
        plone_user1 = _getAuthenticatedUser(self.portal)
        self.assertTrue(isinstance(plone_user1, PloneUser))
        self.assertEqual(plone_user1.id, "acl_users")
        self.assertEqual(plone_user1.getId(), "test_user_1_")
        self.assertEqual(
            sorted(self.catalog._listAllowedRolesAndUsers(plone_user1)),
            ['Anonymous', 'Authenticated', 'Manager', 'user:AuthenticatedUsers', 'user:test_user_1_'])
        login(self.portal, new_user.getId())
        plone_user2 = _getAuthenticatedUser(self.portal)
        self.assertTrue(isinstance(plone_user2, PloneUser))
        self.assertEqual(plone_user2.id, "acl_users")
        self.assertEqual(plone_user2.getId(), "new_user")
        self.assertEqual(
            sorted(self.catalog._listAllowedRolesAndUsers(plone_user2)),
            ['Anonymous', 'Authenticated', 'Manager', 'Member', 'user:Administrators', 'user:AuthenticatedUsers',
             'user:new_user'])
        # as Anonymous
        logout()
        anon_user = _getAuthenticatedUser(self.portal)
        self.assertEqual(
            self.catalog._listAllowedRolesAndUsers(anon_user),
            ['Anonymous'])
