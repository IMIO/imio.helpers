# -*- coding: utf-8 -*-
"""Base module for unittesting."""
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import login
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.testing import z2

import imio.helpers
import logging
import sys
import unittest


def testing_logger(logger_name=''):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


class PloneWithHelpersLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        """Set up Zope."""
        # Load ZCML
        self.loadZCML(
            package=imio.helpers,
            name='testing.zcml'
        )

    def setUpPloneSite(self, portal):
        """Set up Plone."""
        # Install into Plone site using portal_setup
        applyProfile(portal, 'imio.helpers:testing')

        # Login and create some test content
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)
        folder_id = portal.invokeFactory('Folder', 'folder')
        portal[folder_id].reindexObject()
        folder2_id = portal.invokeFactory('Folder', 'folder2')
        portal[folder2_id].reindexObject()

        # Commit so that the test browser sees these objects
        import transaction
        transaction.commit()

    def tearDownZope(self, app):
        """Tear down Zope."""
        z2.uninstallProduct(app, 'imio.helpers')


FIXTURE = PloneWithHelpersLayer(
    name="FIXTURE"
)


INTEGRATION = IntegrationTesting(
    bases=(FIXTURE,),
    name="INTEGRATION"
)


FUNCTIONAL = FunctionalTesting(
    bases=(FIXTURE,),
    name="FUNCTIONAL"
)


class IntegrationTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = INTEGRATION

    def setUp(self):
        super(IntegrationTestCase, self).setUp()
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()
        self.catalog = self.portal.portal_catalog
