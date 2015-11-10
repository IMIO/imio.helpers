# -*- coding: utf-8 -*-

from imio.helpers.cache import cleanVocabularyCacheFor
from imio.helpers.cache import cleanRamCache
from imio.helpers.cache import cleanRamCacheFor
from imio.helpers.testing import IntegrationTestCase
from zope.component import queryUtility
from zope.schema.interfaces import IVocabularyFactory
from plone.memoize import ram
from plone.memoize.instance import Memojito

memPropName = Memojito.propname


def ramCachedMethod_cachekey(method, portal, param):
    '''cachekey method for ramCachedMethod.'''
    return param


@ram.cache(ramCachedMethod_cachekey)
def ramCachedMethod(portal, param):
    """ """
    return portal.REQUEST.get('ramcached', None)


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
