# -*- coding: utf-8 -*-
"""Base module for unittesting."""
from imio.helpers.cache import setup_ram_cache
from imio.helpers.ram import imio_global_cache
from imio.helpers.ram import IMIORAMCache
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
from zope.component import getSiteManager
from zope.component import getUtility
from zope.ramcache.interfaces.ram import IRAMCache

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
        applyProfile(portal, 'collective.MockMailHost:default')

        # use intranet_workflow for every types
        portal.portal_workflow.setDefaultChain('intranet_workflow')
        # Login and create some test content
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)
        folder_id = portal.invokeFactory('Folder', 'folder')
        portal[folder_id].reindexObject()
        folder2_id = portal.invokeFactory('Folder', 'folder2')
        portal[folder2_id].reindexObject()

        if not isinstance(getUtility(IRAMCache), IMIORAMCache):
            sml = getSiteManager(portal)
            sml.unregisterUtility(provided=IRAMCache)
            sml.registerUtility(component=imio_global_cache, provided=IRAMCache)
            setup_ram_cache()

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


class CommonTestCase(unittest.TestCase):

    def setUp(self):
        super(CommonTestCase, self).setUp()
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()
        self.request = self.portal.REQUEST
        self.catalog = self.portal.portal_catalog


class IntegrationTestCase(CommonTestCase):
    """Base class for integration tests."""

    layer = INTEGRATION


class FunctionalTestCase(CommonTestCase):
    """Base class for functional tests."""

    layer = FUNCTIONAL
