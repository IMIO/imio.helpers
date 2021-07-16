# -*- coding: utf-8 -*-

from imio.helpers.content import get_vocab
from imio.helpers.testing import IntegrationTestCase
from plone import api


class TestVocabularies(IntegrationTestCase):
    """
    Test vocabularies.
    """

    def test_SortedUsers(self):
        """ """
        api.user.create(email="test@test.org", username="a_new_user", password="secret")
        api.user.create(email="test@test.org", username="b_new_user", password="secret")
        api.user.create(email="test@test.org", username="new_user", password="secret")
        api.user.create(email="test@test.org", username="A_new_user", password="secret")
        api.user.create(email="test@test.org", username="B_new_user", password="secret")
        vocab = get_vocab(self.portal, "imio.helpers.SortedUsers")
        self.assertEqual(
            [term.title for term in vocab._terms],
            [u'a_new_user (a_new_user)',
             u'A_new_user (A_new_user)',
             u'b_new_user (b_new_user)',
             u'B_new_user (B_new_user)',
             u'new_user (new_user)',
             u'test_user_1_ (test_user_1_)'])
