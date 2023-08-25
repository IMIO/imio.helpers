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
        self.assertTrue(load_workflow_from_package(
            'intranet_workflow', 'profile-Products.CMFPlone:plone'))
        wkf_obj = wkf_tool.get('intranet_workflow')
        states = wkf_obj.states
        self.assertIn('internal', states)
        # not found WF
        self.assertFalse(load_workflow_from_package(
            'intranet_workflow2', 'profile-Products.CMFPlone:plone'))
        # not found profile_id
        self.assertFalse(load_workflow_from_package(
            'intranet_workflow', 'profile-Products.CMFPlone:plone2'))
        # WF not managed by given profile_id
        self.assertFalse(load_workflow_from_package(
            'comment_review_workflow', 'profile-Products.CMFPlone:plone'))

    def test_load_type_from_package(self):
        types_tool = api.portal.get_tool('portal_types')
        portal_type = types_tool.get('Folder')
        self.assertFalse(portal_type.filter_content_types)
        portal_type.filter_content_types = True
        self.assertTrue(portal_type.filter_content_types)
        self.assertTrue(load_type_from_package(
            'Folder', 'profile-Products.CMFPlone:plone'))
        portal_type = types_tool.get('Folder')
        self.assertFalse(portal_type.filter_content_types)
        # not found portal_type
        self.assertFalse(load_type_from_package(
            'Folder2', 'profile-Products.CMFPlone:plone'))
        # not found profile_id
        self.assertFalse(load_type_from_package(
            'Folder', 'profile-Products.CMFPlone:plone2'))
        # type not managed by given profile_id
        self.assertFalse(load_type_from_package(
            'testingtype', 'profile-Products.CMFPlone:plone'))
        # reimport a Dexterity fti
        self.assertTrue(load_type_from_package(
            'testingtype', 'profile-imio.helpers:testing'))
        # with purge_actions=True
        self.assertTrue(load_type_from_package(
            'testingtype', 'profile-imio.helpers:testing', purge_actions=True))
