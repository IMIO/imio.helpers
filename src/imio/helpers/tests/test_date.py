# -*- coding: utf-8 -*-
from DateTime import DateTime
from imio.helpers.date import formatDate
from imio.helpers.date import int2word
from imio.helpers.date import wordizeDate
from imio.helpers.testing import IntegrationTestCase


class TestDateModule(IntegrationTestCase):
    """
    Test all helper methods of date module.
    """

    def test_wordizeDate(self):
        self.assertEqual(wordizeDate(DateTime(12, 12, 12)),
                         'douze d\xc3\xa9cembre deux mille douze')
        self.assertEqual(wordizeDate(DateTime(11, 11, 11)),
                         'onze novembre deux mille onze')
        self.assertEqual(wordizeDate(DateTime(1989, 9, 19)),
                         'dix-neuf septembre mille neuf cent quatre-vingt-neuf')
        self.assertEqual(wordizeDate(DateTime(1, 1, 1)),
                         'premier janvier deux mille un')
        self.assertEqual(wordizeDate(DateTime(12, 12, 12, 12, 12), long_format=True),
                         'douze d\xc3\xa9cembre deux mille douze \xc3\xa0 douze heures douze')
        self.assertEqual(wordizeDate(DateTime(12, 12, 12, 12), long_format=True),
                         'douze d\xc3\xa9cembre deux mille douze \xc3\xa0 douze heures')
        self.assertEqual(wordizeDate(DateTime(1, 1, 1, 1), long_format=True),
                         'premier janvier deux mille un \xc3\xa0 une heure')
        self.assertEqual(wordizeDate(DateTime(1, 1, 1, 0, 1), long_format=True),
                         'premier janvier deux mille un \xc3\xa0 z\xc3\xa9ro heure un')

    def test_formatDate(self):
        self.assertEqual(formatDate("now", month_name=False), DateTime().strftime("%d/%m/%Y"))
        self.assertEqual(formatDate(DateTime(2, 1, 1, 1, 1), month_name=True, long_format=True),
                         u'1er janvier 2002 (01:01)')
        self.assertEqual(formatDate(DateTime(1, 1, 1, 1, 1), month_name=True, long_format=True),
                         u'1er janvier 2001 (01:01)')

    def test_int2word(self):
        self.assertEqual(int2word(21), "vingt et un")
        self.assertEqual(int2word(100), "cent")
        self.assertEqual(int2word(220), "deux cent vingt")
        self.assertEqual(int2word(1000100), "un million cent")
        self.assertEqual(int2word(123456789876543212345678987654321),
                         "cent vingt-trois octilliard quatre cent cinquante-six "
                         "septilliard sept cent quatre-vingt-neuf sextilliard huit "
                         "cent septante-six quintillard cinq cent quarante-trois "
                         "quadrilliard deux cent douze trilliard trois cent quarante-cinq "
                         "billiard six cent septante-huit milliard neuf cent quatre-vingt-sept "
                         "million six cent cinquante-quatre mille trois cent vingt et un")
