# -*- coding: utf-8 -*-
from imio.helpers.setup import load_type_from_package
from imio.helpers.setup import load_workflow_from_package
from imio.helpers.testing import IntegrationTestCase
from plone import api


class TestSetupModule(IntegrationTestCase):
    """
    Test all helper methods of setup module.
    """

    def setUp(self):
        self.portal = self.layer['portal']

    def test_load_workflow_from_package(self):
        wkf_tool = api.portal.get_tool('portal_workflow')
        wkf_obj = wkf_tool.get('intranet_workflow')
        states = wkf_obj.states
        self.assertIn('internal', states)
        states.deleteStates(['internal'])
        self.assertNotIn('internal', states)
        self.assertTrue(load_workflow_from_package('intranet_workflow', 'profile-Products.CMFPlone:plone'))
        wkf_obj = wkf_tool.get('intranet_workflow')
        states = wkf_obj.states
        self.assertIn('internal', states)

    def test_load_type_from_package(self):
        types_tool = api.portal.get_tool('portal_types')
        portal_type = types_tool.get('Folder')
        self.assertFalse(portal_type.filter_content_types)
        portal_type.filter_content_types = True
        self.assertTrue(portal_type.filter_content_types)
        self.assertTrue(load_type_from_package('Folder', 'profile-Products.CMFPlone:plone'))
        portal_type = types_tool.get('Folder')
        self.assertFalse(portal_type.filter_content_types)
