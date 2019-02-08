# -*- coding: utf-8 -*-

from datetime import datetime
from imio.helpers.cache import _generate_params_key
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
from plone import api
from plone.memoize import ram
from plone.memoize.instance import Memojito
from zope.component import queryUtility
from zope.schema.interfaces import IVocabularyFactory


memPropName = Memojito.propname


def ramCachedMethod_cachekey(method, portal, param):
    '''cachekey method for ramCachedMethod.'''
    return param


@ram.cache(ramCachedMethod_cachekey)
def ramCachedMethod(portal, param):
    """ """
    return portal.REQUEST.get('ramcached', None)


@volatile_cache_without_parameters
def volatile_without_parameters_cached(portal):
    return portal.REQUEST.get('volatile_without_parameters_cached', None)


@volatile_cache_with_parameters
def volatile_with_parameters_cached(portal, param):
    return portal.REQUEST.get('volatile_with_parameters_cached', None)


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
        # if get_cachekey_volatile is called and volatile does not exist, it is created with datetime.now()
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
