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
from imio.helpers.cache import VOLATILE_ATTR
from imio.helpers.cache import volatile_cache_with_parameters
from imio.helpers.cache import volatile_cache_without_parameters
from imio.helpers.testing import IntegrationTestCase
from persistent.mapping import PersistentMapping
from plone import api
from plone.memoize import forever
from plone.memoize import ram
from plone.memoize.instance import Memojito
from plone.memoize.interfaces import ICacheChooser
from zope.component import getUtility
from zope.component import queryUtility
from zope.schema.interfaces import IVocabularyFactory


memPropName = Memojito.propname


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
        self.portal.REQUEST.set('vocab_values', ('1', '2'))
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
        self.portal.REQUEST.set('vocab_values', ('1', '2', '3'))
        self.assertEquals([term.token for term in vocab(self.portal)._terms],
                          ['1', '2'])
        # clean vocabulary cache
        cleanVocabularyCacheFor("imio.helpers.testing.testingvocabulary")
        self.assertEquals([term.token for term in vocab(self.portal)._terms],
                          ['1', '2', '3'])

        # every existing vocabularies can also be cleaned if nothing passed to cleanVocabularyCacheFor
        self.portal.REQUEST.set('vocab_values', ('1', '2', '3', '4'))
        self.assertEquals([term.token for term in vocab(self.portal)._terms],
                          ['1', '2', '3'])
        # clean vocabulary cache
        cleanVocabularyCacheFor("imio.helpers.testing.testingvocabulary")
        self.assertEquals([term.token for term in vocab(self.portal)._terms],
                          ['1', '2', '3', '4'])

        # if cleanVocabularyCacheFor is called without parameter,
        # every registered vocabularies cache is cleaned
        self.portal.REQUEST.set('vocab_values', ('1', '2', '3', '4', '5'))
        self.assertEquals([term.token for term in vocab(self.portal)._terms],
                          ['1', '2', '3', '4'])
        cleanVocabularyCacheFor()
        self.assertEquals([term.token for term in vocab(self.portal)._terms],
                          ['1', '2', '3', '4', '5'])

    def test_cleanRamCache(self):
        """
        This helper method invalidates all ram.cache.
        """
        self.portal.REQUEST.set('ramcached', 'a')
        self.assertEquals(ramCachedMethod(self.portal, param='1'), 'a')
        # change value in REQUEST, as it is ram cached, it will still return 'a'
        self.portal.REQUEST.set('ramcached', 'b')
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
        self.portal.REQUEST.set('ramcached', 'a')
        self.assertEquals(ramCachedMethod(self.portal, param='1'), 'a')
        # change value in REQUEST, as it is ram cached, it will still return 'a'
        self.portal.REQUEST.set('ramcached', 'b')
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

        class Foo(object):

            def bar(self):
                pass

        self.assertEqual(
            'imio.helpers.tests.test_cache.Foo.bar',
            generate_key(Foo.bar),
        )

    def test_volatile_cache_without_parameters(self):
        """Helper cache @volatile_cache_without_parameters"""
        generate_key(volatile_without_parameters_cached)
        self.portal.REQUEST.set('volatile_without_parameters_cached', 'a')
        self.assertEqual('a', volatile_without_parameters_cached(self.portal))
        self.portal.REQUEST.set('volatile_without_parameters_cached', 'b')
        self.assertEqual('a', volatile_without_parameters_cached(self.portal))
        # Test invalidation
        invalidate_cachekey_volatile_for(
            generate_key(volatile_without_parameters_cached),
        )
        self.assertEqual('b', volatile_without_parameters_cached(self.portal))

    def test_volatile_cache_with_parameters(self):
        """Helper cache @volatile_cache_with_parameters"""
        self.portal.REQUEST.set('volatile_with_parameters_cached', 'a')
        self.assertEqual(
            'a',
            volatile_with_parameters_cached(self.portal, 'a'),
        )
        self.portal.REQUEST.set('volatile_with_parameters_cached', 'b')
        self.assertEqual(
            'a',
            volatile_with_parameters_cached(self.portal, 'a'),
        )
        self.assertEqual(
            'b',
            volatile_with_parameters_cached(self.portal, 'b'),
        )
        self.portal.REQUEST.set('volatile_with_parameters_cached', 'c')
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
