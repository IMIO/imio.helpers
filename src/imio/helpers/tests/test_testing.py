# -*- coding: utf-8 -*-

from imio.helpers.testing import IntegrationTestCase
from imio.helpers.testing import testing_logger


class TestTesting(IntegrationTestCase):
    """
    Test all helper methods of testing.py module.
    """

    def test_testing_logger(self):
        logger = testing_logger('imio.helpers: testing')
        logger.info('Testing logger info')
        logger.warning('Testing logger warning')
        logger.error('Testing logger error')
