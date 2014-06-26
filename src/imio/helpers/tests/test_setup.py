# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""

from imio.helpers.testing import IntegrationTestCase
from plone import api


class TestInstall(IntegrationTestCase):
    """Test installation of imio.helpers into Plone."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if imio.helpers is installed with portal_quickinstaller."""
        self.assertTrue(self.installer.isProductInstalled('imio.helpers'))

    def test_uninstall(self):
        """Test if imio.helpers is cleanly uninstalled."""
        self.installer.uninstallProducts(['imio.helpers'])
        self.assertFalse(self.installer.isProductInstalled('imio.helpers'))

    # browserlayer.xml
    def test_browserlayer(self):
        """Test that IImioHelpersLayer is registered."""
        from imio.helpers.interfaces import IImioHelpersLayer
        from plone.browserlayer import utils
        self.assertIn(IImioHelpersLayer, utils.registered_layers())
