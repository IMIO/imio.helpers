# -*- coding: utf-8 -*-
from imio.helpers.content import get_vocab
from imio.helpers.testing import IntegrationTestCase
from plone import api
from zope.schema.tests.test_vocabulary import SimpleTermTests


class TestVocabularies(IntegrationTestCase):
    """
    Test vocabularies.
    """

    def test_SortedUsers(self):
        """ """
        api.user.create(email="test@test.org", username="a_new_user", password="secret1234")
        api.user.create(email="test@test.org", username="b_new_user", password="secret1234")
        api.user.create(email="test@test.org", username="new_user", password="secret1234")
        api.user.create(email="test@test.org", username="A_new_user", password="secret1234")
        api.user.create(email="test@test.org", username="B_new_user", password="secret1234")
        vocab = get_vocab(self.portal, "imio.helpers.SortedUsers")
        self.assertEqual(
            [term.title for term in vocab._terms],
            [u'a_new_user (a_new_user)',
             u'A_new_user (A_new_user)',
             u'b_new_user (b_new_user)',
             u'B_new_user (B_new_user)',
             u'new_user (new_user)',
             u'test_user_1_ (test_user_1_)'])
        vocab2 = get_vocab(self.portal, "imio.helpers.SimplySortedUsers")
        self.assertEqual(
            [term.title for term in vocab2._terms],
            [u'a_new_user',
             u'A_new_user',
             u'b_new_user',
             u'B_new_user',
             u'new_user',
             u'test_user_1_'])
        member = api.user.get(username="a_new_user")
        member.setMemberProperties({'fullname': 'anew User'})
        vocab = get_vocab(self.portal, "imio.helpers.SortedUsers")
        vocab2 = get_vocab(self.portal, "imio.helpers.SimplySortedUsers")
        self.assertEqual(
            [term.title for term in vocab._terms],
            [u'anew User (a_new_user)',
             u'A_new_user (A_new_user)',
             u'b_new_user (b_new_user)',
             u'B_new_user (B_new_user)',
             u'new_user (new_user)',
             u'test_user_1_ (test_user_1_)'])
        self.assertEqual(
            [term.title for term in vocab2._terms],
            [u'anew User',
             u'A_new_user',
             u'b_new_user',
             u'B_new_user',
             u'new_user',
             u'test_user_1_'])

    def test_YesNoForFacetedVocabulary(self):
        """ """
        vocab = get_vocab(self.portal, "imio.helpers.YesNoForFacetedVocabulary")
        self.assertEqual(
            [term.value for term in vocab._terms],
            ['0', '1'])
        self.assertEqual(
            [term.title for term in vocab._terms],
            ['yesno_value_false', 'yesno_value_true'])


class EnhancedTermTests(SimpleTermTests):
    """Inherited class tests are also called"""

    def _getTargetClass(self):
        from imio.helpers.vocabularies import EnhancedTerm
        return EnhancedTerm

    def test_attrs(self):
        term = self._makeOne(u'value', title=u'title')
        self.assertDictEqual(term.attrs, {})
        term = self._makeOne(u'value', title=u'title', attr1=u'attr1')
        self.assertDictEqual(term.attrs, {'attr1': u'attr1'})
